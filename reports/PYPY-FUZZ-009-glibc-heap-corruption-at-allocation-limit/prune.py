#!/usr/bin/env python3
"""Coarse-to-fine line-chunk pruner driven by predicate.interesting().

Byte-level reducers stall on this bug: the crash needs the process to be near RLIMIT_AS,
so removing allocations can kill it for reasons unrelated to the corruption. Chunk pruning
at decreasing granularity keeps whole allocation-shaped blocks intact.
"""
import ast, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predicate import interesting

SRC = sys.argv[1]
OUT = sys.argv[2]
WORK = OUT + ".cand"

lines = open(SRC).read().splitlines(True)
print("start: %d lines" % len(lines), flush=True)


def ok(cand):
    text = "".join(cand)
    try:
        ast.parse(text)
    except SyntaxError:
        return False
    open(WORK, "w").write(text)
    return interesting(WORK)


t0 = time.time()
n = len(lines)
size = max(1, n // 2)
while size >= 1:
    i = 0
    removed_this_pass = 0
    while i < len(lines):
        cand = lines[:i] + lines[i + size:]
        if len(cand) != len(lines) and ok(cand):
            removed_this_pass += len(lines) - len(cand)
            lines = cand
            open(OUT, "w").write("".join(lines))
        else:
            i += size
    print("chunk=%-5d -> %5d lines (removed %d, %.0fs)"
          % (size, len(lines), removed_this_pass, time.time() - t0), flush=True)
    if size == 1:
        break
    size = max(1, size // 2)

open(OUT, "w").write("".join(lines))
print("FINAL: %d lines in %s (%.0fs)" % (len(lines), OUT, time.time() - t0), flush=True)
