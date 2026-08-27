"""PyPy 3.11 (7.3.23): SIGILL in the child after fork() from a non-main thread.

    $ pypy3.11 repro.py      # sets RLIMIT_AS itself and repeats; no ulimit needed

    Fatal Python error: Illegal instruction

      File ".../pypy3.11/_weakrefset.py",                 line 122 in discard
      File ".../pypy3.11/threading.py",                   line 1630 in _after_fork
      File ".../pypy3.11/multiprocessing/popen_fork.py",  line 62 in _launch
      File ".../pypy3.11/multiprocessing/popen_fork.py",  line 15 in __init__
      File ".../pypy3.11/threading.py",                   line 971 in run

`_launch` line 62 is its `os.fork()`. PyPy runs the after-fork hooks in the child, so
`threading._after_fork()` executes there and dies walking a weakref set. The whole stack is
ordinary Python; an illegal instruction underneath it means either an RPython `ll_assert`
compiled to a trap or JIT-emitted code running in a state that no longer holds. Forking away
from a multi-threaded, JIT-warm process is exactly such a state.

CPython under an identical limit finishes cleanly (3/3 on the original).

THIS ONE IS PROBABILISTIC, AND THAT IS INHERENT
------------------------------------------------
It is a race -- fork() against the other threads' state -- so the smaller the script, the
smaller the race window and the lower the hit rate:

    11735 lines (the untouched fusil script)   6/6, 8/8
     3481 lines                                6/6
     2020 lines                                5/6
      421 lines                                3/8
      109 lines (fully reduced)                2/10

Hence this driver repeats rather than running once, and reports a rate rather than a verdict.

A REDUCTION HAZARD WORTH REMEMBERING
-------------------------------------
A single-run interestingness test is WRONG for a bug like this: it reads "no crash this run"
as "not interesting" and deletes load-bearing code. Driven by one, the reducer confidently
converged on a 270-line "answer" that reproduces 0/6 -- a dead file. Re-measuring the whole
chain showed the rot started around 2000 lines, so everything below that had been decided on
single-run evidence. The reduction was redone from the last trustworthy point with
`predicate_rep.py`, which accepts on the first hit in four runs; that run produced the
109-line case here, with sound decisions all the way down.

The other trap, specific to this crash: the usual "truncate everything after the crash
marker" shortcut DESTROYS it. Cut the original to 10560 of 11735 lines, just past the
crashing call, and it is clean 3/3 -- the forked children go on executing code that appears
*after* the marker, so that code is load-bearing. It has to be reduced by predicate, never
by position.

Hand-synthesis does not work here either; three attempts are recorded in README.md so they
are not retried.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64).
"""

import os
import resource
import subprocess
import sys

CAP_MIB = 3072
RUNS = 12
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [
    ("reduced_popen_fork.py", "109 lines, fully reduced"),
    ("orig_popen_fork.py", "11735 lines, the untouched fusil script"),
]


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (CAP_MIB * 1024 * 1024, resource.RLIM_INFINITY))


def is_sigill(output, returncode):
    return returncode == -4 or "Fatal Python error: Illegal instruction" in output


def run(path):
    proc = subprocess.run(
        [sys.executable, "-u", path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, cwd=HERE, preexec_fn=_limit,
    )
    return is_sigill(proc.stdout.decode("utf-8", "replace"), proc.returncode)


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    print("RLIMIT_AS = %d MiB, %d runs per case\n" % (CAP_MIB, RUNS))

    total = 0
    for name, why in CASES:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print("  %-24s (missing)" % name)
            continue
        hits = sum(run(path) for _ in range(RUNS))
        total += hits
        print("  %-24s %2d/%d SIGILL   (%s)" % (name, hits, RUNS, why))

    print()
    if total:
        print("The crash is a race, so a rate below 1/1 is expected and is not a failed\n"
              "reproduction. On CPython the same scripts finish cleanly at every run.")
        return 1
    print("No SIGILL in any run. Try raising RUNS, or CAP_MIB -- the crash needs the process\n"
          "near its address-space limit, and that band moves between machines and builds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
