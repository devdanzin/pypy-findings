#!/usr/bin/env python3
"""Interestingness test for the RPython CheckError leak out of Formatter_format_string.

Accepts only the leak itself: an RPython-internal CheckError surfacing at application level
as SystemError, with the format-string frame in the RPython traceback. Rejects every other
face this campaign already knows -- the glibc double-free, PyPy's clean exhaustion abort, the
SIGSEGVs, the SIGILL, and the OTHER RPython leaks (OutOfRange from struct, KeyError from the
tokenizer) -- so a reducer cannot drift from this bug onto a neighbouring one.
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
    if "CheckError" not in out:
        return False
    return "Formatter_format_string" in out


if __name__ == "__main__":
    sys.exit(0 if interesting(sys.argv[1]) else 1)
