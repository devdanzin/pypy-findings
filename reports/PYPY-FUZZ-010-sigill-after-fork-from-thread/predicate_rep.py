#!/usr/bin/env python3
"""Repetition-based interestingness test for the fork-from-a-thread SIGILL.

WHY THIS EXISTS. The single-shot `predicate.py` is wrong for this bug. The crash is a race --
fork() racing the other threads' state -- so shrinking the script shrinks the race window and
the hit rate falls with it. A one-run predicate then reads "no crash" as "not interesting" for
a candidate that reproduces 2 times in 6, and the reducer happily deletes load-bearing code.
Measured on the pass outputs of a run driven by the single-shot predicate:

    orig  11735 lines  6/6        pass5   411 lines  2/6
    pass1  3481 lines  6/6        pass6   395 lines  0/6
    pass2  2020 lines  5/6        pass7   360 lines  2/6
    pass3   643 lines  2/6        pass9   285 lines  2/6
    pass4   531 lines  3/6        pass10  270 lines  0/6   <- the "final" answer, dead

Everything from pass3 down was decided on single-run evidence and cannot be trusted.

This predicate runs the candidate up to RUNS times and accepts on the first hit, so a
candidate that reproduces at even ~1-in-4 is kept. It short-circuits, so an interesting
candidate usually still costs one run; only rejections pay the full RUNS.

Usage: predicate_rep.py <script.py>   -> exit 0 if interesting, 1 otherwise.
"""
import sys

from predicate import interesting

RUNS = 4


def interesting_repeated(path, runs=RUNS):
    for _ in range(runs):
        if interesting(path):
            return True
    return False


if __name__ == "__main__":
    sys.exit(0 if interesting_repeated(sys.argv[1]) else 1)
