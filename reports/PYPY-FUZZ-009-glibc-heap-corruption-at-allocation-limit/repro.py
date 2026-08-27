"""PyPy 3.11 (7.3.23): glibc heap corruption at an address-space limit.

    $ pypy3.11 repro.py      # sets RLIMIT_AS itself and sweeps; no ulimit needed

    free(): double free detected in tcache 2
    Fatal Python error: Aborted

PyPy has a clean way of failing when it runs out of address space, and it normally uses it:

    out of memory: couldn't allocate the next arena

This is not that. glibc names the corruption, which means the C heap was already damaged
before the allocator noticed. CPython under an identical limit finishes cleanly.

MEASURED (reduced_functools.py)

    cap        PyPy            CPython 3.14
    1024 MiB   clean 3/3       clean 4/4
    1536 MiB   CORRUPT 3/3     -
    2048 MiB   clean 3/3       clean 4/4
    2560 MiB   clean 3/3       -
    3072 MiB   CORRUPT 3/3     clean 4/4      (8/8 on a longer run)
    3584 MiB   clean 3/3       -
    4096 MiB   clean 3/3       clean 4/4

Deterministic inside a window, but there is more than one window and each is narrow -- one
step either way and it is clean. That is why this script SWEEPS instead of hardcoding a
number: a four-point sweep over 1024/2048/3072/4096 finds 3072 and misses 1536 entirely. The
bands depend on where this build's own reservations land, so they move between machines and
between PyPy versions.

THREE DIFFERENT THINGS HAPPEN AT AN ALLOCATION LIMIT
----------------------------------------------------
Worth stating explicitly, because they are easy to conflate and only the third is this bug:

    "out of memory: couldn't allocate ..."   PyPy's intended clean failure
    SIGSEGV                                  a separate finding (gc of cyclic finalizables,
                                             and ThreadPool construction)
    free(): double free / corruption         THIS -- actual C-heap damage

Measured across five caps on the SIGSEGV case, PyPy's aborts are *always* the clean message,
never a glibc one. So these really are distinct outcomes, not one bug wearing three faces.

MECHANISM: UNKNOWN
------------------
Two hypotheses were tested and both are dead:

  * Failed thread creation. The original session shows `Failed to create thread ...:
    MemoryError` just before the abort, so a mishandled thread-bootstrap allocation looked
    likely -- and would also have explained the ThreadPool SIGSEGV. It does not hold: starting
    4000 threads under RLIMIT_AS 3072 MiB with 0-3000 MiB of ballast produced no corruption on
    PyPy or CPython at any ballast level.

  * libmpdec through cffi. The reduced script builds huge `Decimal`s from a 4299-digit int,
    and cffi-wrapped C libraries do use real malloc/free -- but PyPy has no `_decimal` module
    at all (`ModuleNotFoundError`), so that code takes the pure-Python `decimal` fallback and
    no foreign allocator is involved.

REPRODUCED IN TWO UNRELATED MODULES
-----------------------------------
fusil produced the same face from `functools` and from `importlib.resources._common` in
different fleet instances, which is what argues this is interpreter-level rather than
something about one module. `trunc_importlib.py` (2/2) is kept alongside as the second
witness.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64), reduced from a 21624-line
generated script to 247 lines by `prune.py` under `predicate.py`.
"""

import os
import resource
import subprocess
import sys

CAPS_MIB = [1024, 1536, 2048, 2560, 3072, 3584, 4096]
RUNS_PER_CAP = 3
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.join(HERE, "reduced_functools.py")
GLIBC_MARKERS = ("free():", "double free", "corruption", "malloc():")


def _limit(cap_mib):
    def apply():
        resource.setrlimit(
            resource.RLIMIT_AS, (cap_mib * 1024 * 1024, resource.RLIM_INFINITY)
        )

    return apply


def classify(output, returncode):
    if any(marker in output for marker in GLIBC_MARKERS):
        return "HEAP CORRUPTION"
    if "out of memory" in output:
        return "clean oom abort"
    if returncode == -11:
        return "SIGSEGV"
    if returncode == -6:
        return "abort"
    return "clean"


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    if not os.path.exists(CASE):
        sys.exit("reduced_functools.py not found next to this script")
    print("running reduced_functools.py under a range of RLIMIT_AS caps, %d runs each\n"
          % RUNS_PER_CAP)

    corrupt = 0
    for cap_mib in CAPS_MIB:
        outcomes = {}
        for _ in range(RUNS_PER_CAP):
            proc = subprocess.run(
                [sys.executable, "-u", CASE],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, cwd=HERE,
                preexec_fn=_limit(cap_mib),
            )
            verdict = classify(proc.stdout.decode("utf-8", "replace"), proc.returncode)
            outcomes[verdict] = outcomes.get(verdict, 0) + 1
        corrupt += outcomes.get("HEAP CORRUPTION", 0)
        print("  cap %5d MiB -> %s" % (cap_mib, ", ".join(
            "%s %d/%d" % (k, v, RUNS_PER_CAP) for k, v in sorted(outcomes.items()))))

    print()
    if corrupt:
        print("%d run(s) corrupted the C heap. PyPy's own exhaustion abort prints\n"
              "\"out of memory: couldn't allocate the next arena\"; glibc naming the\n"
              "corruption instead means the heap was already damaged." % corrupt)
        return 1
    print("No corruption anywhere in the sweep. The window is narrow and depends on where\n"
          "this build's reservations sit -- widen CAPS_MIB, or step it more finely near the\n"
          "point where the runs stop finishing cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
