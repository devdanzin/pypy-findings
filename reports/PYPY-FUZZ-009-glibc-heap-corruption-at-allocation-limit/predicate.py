#!/usr/bin/env python3
"""STRICT interestingness test for the PyPy glibc double-free.

Accepts ONLY the heap-corruption abort:
  * the process must die on SIGABRT (returncode -6),
  * glibc must name the corruption ("free():" / "double free" / "corruption" / "malloc():"),
  * PyPy's own CLEAN exhaustion abort ("out of memory: ...") must NOT appear -- that is the
    benign outcome this bug is distinguished from,
  * no SIGSEGV / SIGKILL / timeout may be accepted either: those are DIFFERENT findings
    (the ThreadPool and gc-at-exhaustion segfaults), and accepting them lets a reducer
    drift onto the wrong bug.

Usage: predicate.py <script.py>   -> exit 0 if interesting, 1 otherwise.
"""
import os, resource, subprocess, sys

PYPY = "/home/danzin/.local/share/uv/python/pypy-3.11.15-linux-x86_64-gnu/bin/pypy3.11"
CAP_MIB = 3072
TIMEOUT = 120
GLIBC = ("free():", "double free", "corruption", "malloc():")


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
    if p.returncode != -6:
        return False
    if "out of memory" in out:
        return False
    return any(m in out for m in GLIBC)


if __name__ == "__main__":
    sys.exit(0 if interesting(sys.argv[1]) else 1)
