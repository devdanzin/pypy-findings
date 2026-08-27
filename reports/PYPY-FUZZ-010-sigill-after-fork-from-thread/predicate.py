#!/usr/bin/env python3
"""STRICT interestingness test for the PyPy fork-from-a-thread SIGILL.

Accepts ONLY the illegal-instruction face:
  * the process (or a forked child whose status the harness sees) must die on SIGILL, or
    faulthandler must have printed "Fatal Python error: Illegal instruction",
  * every OTHER crash face this campaign already knows must be rejected -- the glibc
    double-free, PyPy's clean exhaustion abort, and the SIGSEGVs of findings #6/#7 -- so a
    reducer cannot drift from this bug onto one of those.

Usage: predicate.py <script.py>   -> exit 0 if interesting, 1 otherwise.
"""
import os, resource, subprocess, sys

PYPY = "/home/danzin/.local/share/uv/python/pypy-3.11.15-linux-x86_64-gnu/bin/pypy3.11"
CAP_MIB = 3072
TIMEOUT = 240


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (CAP_MIB * 1024 * 1024, resource.RLIM_INFINITY))


def interesting(path):
    try:
        p = subprocess.run(
            [PYPY, "-u", path], capture_output=True, text=True, timeout=TIMEOUT,
            stdin=subprocess.DEVNULL, preexec_fn=_limit,
            cwd=os.path.dirname(os.path.abspath(path)) or ".",
        )
    except subprocess.TimeoutExpired:
        return False
    out = p.stdout + p.stderr
    # Reject the neighbouring findings outright.
    if "double free" in out or "free():" in out or "corruption" in out:
        return False
    if "out of memory" in out:
        return False
    if "Fatal Python error: Segmentation fault" in out or p.returncode == -11:
        return False
    return p.returncode == -4 or "Fatal Python error: Illegal instruction" in out


if __name__ == "__main__":
    sys.exit(0 if interesting(sys.argv[1]) else 1)
