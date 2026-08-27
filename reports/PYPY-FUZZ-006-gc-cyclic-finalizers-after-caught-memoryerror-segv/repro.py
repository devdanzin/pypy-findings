"""PyPy 3.11 (7.3.23): SIGSEGV collecting cyclic finalizable objects at address-space exhaustion.

    $ pypy3.11 repro.py      # sets RLIMIT_AS itself and sweeps; no ulimit needed

The minimal case (`minimal.py` next to this file), under `ulimit -v 3145728`:

    import gc, weakref
    class D:
        def __del__(self): pass
    def make():
        a = D(); b = D(); a.o = b; b.o = a; return a
    keep = []
    try:
        while True:
            keep.append(make())
    except MemoryError:
        pass
    for _ in range(30):
        gc.collect()

    PyPy 7.3.23 : SIGSEGV, 6/6
    CPython 3.14: exits cleanly, 6/6

The MemoryError is caught, so at that point the program is in a state Python defines as
recoverable. Collecting the cycles then segfaults instead of raising. There is no benign
`out of memory: couldn't allocate ...` message -- that is PyPy's *clean* exhaustion abort,
and its absence is what distinguishes this from mere OOM.

EVERY LINE IS LOAD-BEARING (measured, 4 runs each):

    as written                      4/4 segv
    without `def __del__`           0/4      finalizers are required
    without the reference cycle     0/4      cycle collection is required
    without the gc.collect() loop   0/4      the crash is in collection
    without `import weakref`        0/4      <-- and weakref is never USED

That last one is the interesting one, and the reason this script sweeps. `weakref` is
imported and never referenced, so it can only be affecting the heap -- PyPy handles weakrefs
specially during collection, so importing the module is not neutral. It is not simply "more
bytes" either: substituting a bytearray of 64 KiB .. 2 MiB gives 0/4, as do
`[object() for _ in range(20000)]`, `[{} for _ in range(20000)]`, and `import functools`
(`import types` manages 1/4). The crash sits on a threshold in the GC heap's *shape*, not its
size.

Because of that, a fixed script is fragile across machines and PyPy builds. This driver runs
the minimal case under a range of address-space caps and reports which ones segfault.

Originally found by fusil inside a 22125-line generated script whose last output before the
segfault was an explicit `gc.collect()`, at a measured peak VmSize of 3071 MiB against a
3072 MiB cap.
"""

import os
import resource
import subprocess
import sys

CAPS_MIB = [1024, 1536, 2048, 3072, 4096]
RUNS_PER_CAP = 4
MINIMAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minimal.py")


def _limit(cap_mib):
    def apply():
        resource.setrlimit(
            resource.RLIMIT_AS, (cap_mib * 1024 * 1024, resource.RLIM_INFINITY)
        )

    return apply


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    if not os.path.exists(MINIMAL):
        sys.exit("minimal.py not found next to this script")
    print("running minimal.py under a range of RLIMIT_AS caps, %d runs each\n" % RUNS_PER_CAP)

    total = 0
    for cap_mib in CAPS_MIB:
        segfaults = clean = aborts = 0
        for _ in range(RUNS_PER_CAP):
            proc = subprocess.run(
                [sys.executable, "-u", MINIMAL],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                preexec_fn=_limit(cap_mib),
            )
            # subprocess reports a signal as a NEGATIVE returncode: -11 is SIGSEGV.
            if proc.returncode == -11:
                segfaults += 1
            elif proc.returncode == -6:
                aborts += 1
            else:
                clean += 1
        total += segfaults
        print("  cap %5d MiB -> %d segfault, %d abort, %d clean"
              % (cap_mib, segfaults, aborts, clean))

    print()
    if total:
        print("%d segfaults. A caught MemoryError left the program in a state Python calls\n"
              "recoverable; gc.collect() then crashed instead of raising." % total)
        return 1
    print("No segfault at any cap. The window depends on where this build's own reservations\n"
          "sit -- try more caps, or run minimal.py directly under `ulimit -v`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
