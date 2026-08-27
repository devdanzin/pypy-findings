#!/usr/bin/env python3
"""prune.py, driven by the repetition predicate. See predicate_rep.py for why."""
import ast, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predicate_rep import interesting_repeated

SRC, OUT = sys.argv[1], sys.argv[2]
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
    return interesting_repeated(WORK)


t0 = time.time()
size = max(1, len(lines) // 2)
while size >= 1:
    i = 0
    before = len(lines)
    while i < len(lines):
        cand = lines[:i] + lines[i + size:]
        if len(cand) != len(lines) and ok(cand):
            lines = cand
            open(OUT, "w").write("".join(lines))
        else:
            i += size
    print("chunk=%-5d -> %5d lines (removed %d, %.0fs)"
          % (size, len(lines), before - len(lines), time.time() - t0), flush=True)
    if size == 1:
        break
    size = max(1, size // 2)

open(OUT, "w").write("".join(lines))
print("FINAL: %d lines in %s (%.0fs)" % (len(lines), OUT, time.time() - t0), flush=True)
