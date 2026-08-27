"""PyPy 3.11 (7.3.23): two threads calling next() on one file iterator segfaults.

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

WHAT IS REQUIRED: EOF, REACHED CONCURRENTLY, ON THE TEXT LAYER OVER A REAL FD

The threads must actually EXHAUST the iterator -- the fault is at end-of-file, not during
steady-state reading:

    file                       iterations   SIGSEGV
    /dev/null (empty)              200        4/6
    a 1-line file                  200        6/6
    a 5000-line file               200        0/6     <- never reaches EOF
    a 5000-line file            20 000        6/6     <- same file, now exhausted

That is why an empty or tiny file looks so much more "reliable": it reaches EOF on the first
call. The reproducer below therefore drives to EOF explicitly rather than relying on the
file being short.

AND THE OTHER HALF: THE TEXT LAYER *AND* A REAL FILE DESCRIPTOR

Measured, 6 runs per stream kind:

    stream                                          PyPy      CPython
    sys.__stdin__                                   SEGV 6/6  clean
    open("/dev/null")                               SEGV 6/6  clean
    open("/etc/hostname")                           SEGV 6/6  clean
    os.fdopen(os.open("/dev/null", os.O_RDONLY))    SEGV 6/6  clean
    io.TextIOWrapper(io.BytesIO(...))               clean     clean   <- text layer, no fd
    io.BufferedReader(io.FileIO("/dev/null"))       clean     clean   <- fd, no text layer

Neither half crashes alone. That is the interesting part, and it suggests the mechanism:
PyPy releases the GIL around the real `read()` syscall, so two threads can be inside
`TextIOWrapper.__next__` at once and race its decoder / readahead state. A `BytesIO` never
releases the GIL, so the same code is serialised and safe; a `BufferedReader` has the fd but
no text-decoding state to corrupt.

If that reading is right, this is a *missing lock around the text layer's buffer*, not
anything to do with the fd itself -- and the GIL, which makes most PyPy threading safe by
accident, is precisely what stops protecting it here.

TWO THREADS IS ENOUGH

    threads    2     3     4     8
    SIGSEGV  3-4/4 3-4/4  4/4   4/4

It is a race, so the rate is not 1/1 even at eight threads on a busy machine; the shipped
driver reports a rate rather than a verdict for that reason.

HOW IT WAS FOUND

fusil's `--concurrency-stress` mode, fleet_08, as 6 crash dirs on the `sys` module. The
generated scripts print `[CSTRESS] note: GIL enabled; running serialised`, and the mode was
expected to find deadlocks and re-entrancy rather than anything race-shaped, since the GIL
rules out data races -- so a segfault from concurrent iteration was not what the fleet was
looking for.

The 1739-line session script reduced to 335 lines (10/10 under a repetition predicate), and
the surviving fragment named the shape directly: one iterator over `sys.__stdin__` in
`_tsan_iter_factories`, advanced by four workers. An ingredient matrix over the reduced
op-mix then isolated it -- `iter` alone reproduces 4/4, and everything *except* `iter`
(repr, gc, weakref, container mutation, dir) is 0/4.
"""

import os
import subprocess
import sys
import tempfile

CHILD = """
import io, os, sys, threading
_tiny = {tiny!r}
{setup}
it = iter(f)
def w():
    for _ in range(200):
        try:
            next(it)
        except Exception:
            pass
ts = [threading.Thread(target=w) for _ in range({threads})]
for t in ts: t.start()
for t in ts: t.join()
print("survived")
"""

STREAMS = [
    ("sys.__stdin__", "f = sys.__stdin__", True),
    ('open("/dev/null")', 'f = open("/dev/null")', True),
    ("open(<1-line file>)", "f = open(_tiny)", True),
    ("os.fdopen(os.open(...))", 'f = os.fdopen(os.open("/dev/null", os.O_RDONLY))', True),
    ("TextIOWrapper(BytesIO)", 'f = io.TextIOWrapper(io.BytesIO(b"a\\nb\\n" * 500))', False),
    ("BufferedReader(FileIO)", 'f = io.BufferedReader(io.FileIO("/dev/null"))', False),
]
RUNS = 6


def run(setup, threads=2, tiny=None):
    proc = subprocess.run(
        [sys.executable, "-c",
         CHILD.format(setup=setup, threads=threads, tiny=tiny or os.devnull)],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    return proc.returncode == -11


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    tiny = os.path.join(tempfile.mkdtemp(), "one_line.txt")
    with open(tiny, "w") as fh:
        fh.write("one line\n")
    header = "%-30s %-10s %s" % ("stream", "expected", "SIGSEGV")
    print(header)
    print("-" * len(header))

    faults = 0
    for label, setup, should_fault in STREAMS:
        hits = sum(run(setup, tiny=tiny) for _ in range(RUNS))
        faults += hits
        print("%-30s %-10s %d/%d" % (label, "yes" if should_fault else "no", hits, RUNS))

    print("\nthread count, on open(\"/dev/null\"):")
    for n in (2, 3, 4, 8):
        hits = sum(run('f = open("/dev/null")', n, tiny) for _ in range(4))
        print("  %d threads -> %d/4" % (n, hits))

    print()
    if faults:
        print("Concurrent next() on one file iterator faults. It needs BOTH the text layer\n"
              "and a real file descriptor: neither half alone reproduces it.")
        return 1
    print("No faults. On CPython this is the expected result -- concurrent iteration there is\n"
          "unspecified but does not crash.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
