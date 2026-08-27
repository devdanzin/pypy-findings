#!/usr/bin/env python3
"""Interestingness test for the concurrency-stress SIGSEGV.

Accepts on the first SIGSEGV in RUNS attempts -- the crash is probabilistic (2/4 measured on
the unreduced script), so a single-run predicate would delete load-bearing code, which is the
mistake that cost a whole reduction earlier in this campaign.

Rejects every other face this fleet produces: the glibc netlink abort (fuzzer self-harm via
socket.close(int)), heap-corruption aborts, PyPy's clean exhaustion abort, and the JIT
assertion -- so a reducer cannot drift between them.
"""
import os, resource, subprocess, sys

PYPY = "/home/danzin/.local/share/uv/python/pypy-3.11.15-linux-x86_64-gnu/bin/pypy3.11"
CAP_MIB = 3072
TIMEOUT = 300
RUNS = 4


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (CAP_MIB * 1024 * 1024, resource.RLIM_INFINITY))


def once(path):
    try:
        p = subprocess.run(
            [PYPY, "-u", path], capture_output=True, text=True, timeout=TIMEOUT,
            stdin=subprocess.DEVNULL, preexec_fn=_limit,
            cwd=os.path.dirname(os.path.abspath(path)) or ".",
        )
    except subprocess.TimeoutExpired:
        return False
    out = p.stdout + p.stderr
    if "netlink" in out or "out of memory" in out:
        return False
    if "malloc():" in out or "free():" in out or "double free" in out:
        return False
    if "Fatal RPython error" in out:
        return False
    return p.returncode == -11


def interesting(path, runs=RUNS):
    return any(once(path) for _ in range(runs))


if __name__ == "__main__":
    sys.exit(0 if interesting(sys.argv[1]) else 1)
