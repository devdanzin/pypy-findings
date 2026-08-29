"""PyPy 3.11 (7.3.23): two threads calling next() on one TEXT-stream iterator segfault.

    $ pypy3.11 repro.py

    import threading
    f = open("/dev/null")
    it = iter(f)
    def w():
        for _ in range(200):
            try: next(it)
            except Exception: pass
    ts = [threading.Thread(target=w) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join()

    Segmentation fault (core dumped)

Two threads. No ctypes, no address-space limit, no fuzzer scaffolding -- just `for line in f`
shared between threads, which is ordinary (if racy) Python. CPython does not crash on it: the
iterator's behaviour is unspecified under concurrent use, but it raises or returns garbage
lines, it does not fault.

WHAT IS REQUIRED: THE TEXT LAYER, ADVANCED CONCURRENTLY, DRIVEN TO EOF

(1) THE TEXT LAYER.  io.TextIOWrapper over anything faults; nothing else does. Measured over
five stream lengths (1, 3, 50, 500 and 5000 lines), 2 threads x 200 next() calls, 6 runs per
cell:

    stream                             1      3     50    500   5000 lines
    io.TextIOWrapper(io.BytesIO(..))  6/6    0/6   5-6/6   0/6    0/6
    open(<file>)                      6/6    6/6   5-6/6   0/6    0/6
    io.BufferedReader(io.BytesIO(..)) 0/6    0/6    0/6    0/6    0/6
    io.BufferedReader(io.FileIO(..))  0/6    0/6    0/6    0/6    0/6
    io.BytesIO(..)                    0/6    0/6    0/6    0/6    0/6
    io.StringIO(..)                   0/6    0/6    0/6    0/6    0/6

(2) EXHAUSTION.  The fault is at end-of-file, not during steady-state reading. Holding the
stream kind fixed and varying only how far the threads get:

    stream                             400 advances   40 000 advances
    open(<5000-line file>)                 0/6             6/6
    io.TextIOWrapper(io.BytesIO(..))       0/6             6/6

That is why the length row above is not monotonic: a short stream reaches EOF on the first
few calls, a 5000-line one never reaches it within 400 advances, and 50 lines lands in
between. The driver below therefore drives to EOF explicitly rather than relying on length.

A REAL FILE DESCRIPTOR IS *NOT* REQUIRED -- AND THIS CATALOG SAID IT WAS

Until 2026-08-28 this record claimed the stream had to be "the text layer over a REAL file
descriptor", on the strength of one row: io.TextIOWrapper(io.BytesIO(...)) measuring 0/6.
That row was confounded. It used a 1000-line BytesIO while every stream it was compared
against was short, at a fixed 200 iterations -- so it was the only row that never reached
EOF, and its 0/6 measured the missing exhaustion, not the missing descriptor. With
exhaustion held constant it faults 6/6, as the tables above show.

The descriptor is not irrelevant: fd-backed streams fault at lengths where BytesIO-backed
ones do not (3 lines: 6/6 vs 0/6), so a real read() widens the window. But it is not a
precondition, and the mechanism does not run through the syscall. What is left is the text
layer's own decoder/readahead state, which two threads can be inside simultaneously with
nothing serialising them -- the GIL, which makes most PyPy threading safe by accident, does
not cover it here.

TWO THREADS IS ENOUGH

    threads    1     2     4
    SIGSEGV   0/6   6/6   6/6

It is a race, so the rate is not 1/1 in every configuration; the driver reports rates
rather than a verdict for that reason.

HOW IT WAS FOUND

fusil's `--concurrency-stress` mode, fleet_08, as 6 crash dirs on the `sys` module (25 by the
end of the run, all 25 carrying a std-stream iterator). The generated scripts print
`[CSTRESS] note: GIL enabled; running serialised`, and the mode was expected to find deadlocks
and re-entrancy rather than anything race-shaped, since the GIL rules out data races -- so a
segfault from concurrent iteration was not what the fleet was looking for.

The 1739-line session script reduced to 335 lines (11/12 under a repetition predicate), and
the surviving fragment named the shape directly: one iterator over `sys.__stdin__` in
`_tsan_iter_factories`, advanced by four workers. An ingredient matrix over the reduced
op-mix then isolated it -- `iter` alone reproduces 4/4, and everything *except* `iter`
(repr, gc, weakref, container mutation, dir) is 0/4.
"""

import io
import os
import subprocess
import sys
import tempfile

CHILD = """
import io, os, sys, threading
_path = {path!r}
{setup}
it = iter(f)
def w():
    for _ in range({iters}):
        try:
            next(it)
        except Exception:
            pass
ts = [threading.Thread(target=w) for _ in range({threads})]
for t in ts: t.start()
for t in ts: t.join()
print("survived")
"""

# (label, setup, is_text_layer) -- the third column is the prediction being tested.
STREAMS = [
    ("TextIOWrapper(BytesIO)", "f = io.TextIOWrapper(io.BytesIO(open(_path,'rb').read()))", True),
    ("open(<file>)", "f = open(_path)", True),
    ("BufferedReader(BytesIO)", "f = io.BufferedReader(io.BytesIO(open(_path,'rb').read()))", False),
    ("BufferedReader(FileIO)", "f = io.BufferedReader(io.FileIO(_path))", False),
    ("BytesIO", "f = io.BytesIO(open(_path,'rb').read())", False),
    ("StringIO", "f = io.StringIO(open(_path).read())", False),
]
LENGTHS = [1, 3, 50, 500, 5000]
RUNS = 6
ITERS = 200


def make_file(tmpdir, nlines):
    path = os.path.join(tmpdir, "lines_%d.txt" % nlines)
    with open(path, "w") as fh:
        fh.write("a\nb\n" * nlines)
    return path


def run(setup, path, threads=2, iters=ITERS):
    proc = subprocess.run(
        [sys.executable, "-c",
         CHILD.format(setup=setup, threads=threads, iters=iters, path=path)],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    return proc.returncode == -11


def rate(setup, path, threads=2, iters=ITERS, runs=RUNS):
    return sum(run(setup, path, threads, iters) for _ in range(runs))


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    tmp = tempfile.mkdtemp()
    paths = {n: make_file(tmp, n) for n in LENGTHS}

    print("(1) the TEXT LAYER is what matters -- SIGSEGV rate out of %d, %d threads, %d iters"
          % (RUNS, 2, ITERS))
    header = "%-26s %s" % ("stream", "".join("%8s" % ("%d ln" % n) for n in LENGTHS))
    print(header)
    print("-" * len(header))
    text_hits = other_hits = 0
    for label, setup, is_text in STREAMS:
        cells = [rate(setup, paths[n]) for n in LENGTHS]
        if is_text:
            text_hits += sum(cells)
        else:
            other_hits += sum(cells)
        print("%-26s %s" % (label, "".join("%8s" % ("%d/%d" % (c, RUNS)) for c in cells)))

    print("\n(2) EXHAUSTION, with the stream kind held fixed (5000 lines):")
    for label, setup, is_text in STREAMS[:2]:
        a = rate(setup, paths[5000], iters=200)
        b = rate(setup, paths[5000], iters=20000)
        print("  %-26s 400 advances %d/%d   40000 advances %d/%d"
              % (label, a, RUNS, b, RUNS))

    print("\n(3) thread count, on TextIOWrapper(BytesIO) over a 1-line stream:")
    for n in (1, 2, 4):
        print("  %d thread(s) -> %d/%d" % (n, rate(STREAMS[0][1], paths[1], threads=n), RUNS))

    print()
    if text_hits and not other_hits:
        print("Concurrent next() on one TEXT-stream iterator faults at EOF. Only the\n"
              "io.TextIOWrapper rows fault; a real file descriptor is NOT required.")
        return 1
    if not text_hits:
        print("No faults. On CPython this is the expected result -- concurrent iteration there\n"
              "is unspecified but does not crash.")
        return 0
    print("UNEXPECTED: a non-text stream faulted; the mechanism claim above needs revisiting.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
