"""PyPy 3.11 (7.3.23): SIGSEGV constructing a ThreadPool near an address-space limit.

    $ pypy3.11 repro.py          # sweeps for you; no ulimit needed, it sets RLIMIT_AS itself

A no-argument `multiprocessing.pool.ThreadPool()` segfaults when the worker threads
`Pool.__init__` starts begin to fail against RLIMIT_AS:

    Fatal Python error: Segmentation fault
      File ".../multiprocessing/pool.py", line 183 in __init__      (Pool.__init__)
      File ".../multiprocessing/pool.py", line 929 in __init__      (ThreadPool.__init__)

CPython under an identical limit and ballast raises cleanly instead (0/10 here).

The benign outcome -- which PyPy produces most of the time, and which is presumably the
intended one -- is

    AttributeError: 'DummyProcess' object has no attribute 'terminate'

from `Pool.__init__`'s own cleanup path at pool.py:219. The bug is that the same situation
sometimes segfaults instead.

WHY THIS SCRIPT SWEEPS INSTEAD OF HARDCODING A NUMBER
-----------------------------------------------------
The crash needs the process to sit in a narrow band below the limit: enough address space to
get the pool started, not enough to finish. The band is thin and depends on where PyPy's own
reservations land, so it moves between machines AND between versions of this very file.
Measured here (ulimit -v 3145728, 8-10 runs per point):

    a 4-line script:      375 MiB -> 0     400 MiB -> 6..7/10     425 MiB -> 0
    this file, +docstring: 400 MiB -> 1/8                         550 MiB -> 4/8

Adding this docstring moved the window by 150 MiB. A hardcoded constant is therefore useless
to anyone else, so the script tries a range and reports which values crash. A self-calibrating
variant (fill the address space, then release a fixed headroom) does NOT reproduce it, so the
ballast is not merely a proxy for "nearly full".

Originally found by fusil inside a 22249-line generated script.
"""

import os
import resource
import subprocess
import sys

ADDRESS_SPACE_MIB = 3072
POOLS = 3
SWEEP = range(300, 901, 25)
RUNS_PER_POINT = 4


def child(ballast_mib):
    """Allocate ballast, then build pools until one of them segfaults."""
    ballast = [bytearray(1024 * 1024) for _ in range(ballast_mib)]
    import multiprocessing.pool

    for _ in range(POOLS):
        multiprocessing.pool.ThreadPool()
    return 0 if ballast else 0  # keep the ballast alive to the very end


def _limit():
    resource.setrlimit(
        resource.RLIMIT_AS, (ADDRESS_SPACE_MIB * 1024 * 1024, resource.RLIM_INFINITY)
    )


def parent():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    print("RLIMIT_AS = %d MiB, %d pools per run, %d runs per point\n"
          % (ADDRESS_SPACE_MIB, POOLS, RUNS_PER_POINT))

    total = 0
    for ballast_mib in SWEEP:
        segfaults = 0
        for _ in range(RUNS_PER_POINT):
            proc = subprocess.run(
                [sys.executable, os.path.abspath(__file__), str(ballast_mib)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                preexec_fn=_limit,
            )
            # A signal is reported as a negative returncode; -11 is SIGSEGV.
            if proc.returncode == -11:
                segfaults += 1
        total += segfaults
        if segfaults:
            print("  ballast %4d MiB -> %d/%d SEGFAULT"
                  % (ballast_mib, segfaults, RUNS_PER_POINT))

    if total:
        print("\n%d segfaults total. Re-run one of the crashing values by hand to see the\n"
              "faulthandler stack:\n"
              "    ( ulimit -v %d; %s -c \"import faulthandler,sys; faulthandler.enable();\\\n"
              "        sys.argv=['x','<MiB>']; exec(open('%s').read())\" )"
              % (total, ADDRESS_SPACE_MIB * 1024, sys.executable, os.path.abspath(__file__)))
        return 1

    print("No segfault anywhere in the sweep. Widen SWEEP, or lower ADDRESS_SPACE_MIB --\n"
          "the window depends on where this interpreter's own reservations sit.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(child(int(sys.argv[1])))
    sys.exit(parent())
