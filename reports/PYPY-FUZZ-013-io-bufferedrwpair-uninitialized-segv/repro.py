"""PyPy 3.11 (7.3.23): an uninitialized _io.BufferedRWPair segfaults instead of raising.

    $ pypy3.11 repro.py

    $ pypy3.11 -c 'import _io; _io.BufferedRWPair.__new__(_io.BufferedRWPair).closed'
    Segmentation fault (core dumped)

`T.__new__(T)` builds an instance without running `__init__`, which is ordinary Python and
something pickle, copy and many deserializers do routinely. Every other type in the `_io`
buffered/text family answers that state with

    ValueError: I/O operation on uninitialized object

`BufferedRWPair` is the one that dereferences instead. Measured, one operation per subprocess:

    type              .closed          iter()           .isatty()
    BufferedRWPair    SIGSEGV          SIGSEGV          SIGSEGV
    BufferedRandom    ValueError       ValueError       ValueError
    BufferedReader    ValueError       ValueError       ValueError
    BufferedWriter    ValueError       ValueError       ValueError
    TextIOWrapper     ValueError       ValueError       ValueError
    FileIO            (clean)          ValueError       ValueError
    BytesIO           (clean)          (clean)          (clean)
    StringIO          (clean)          (clean)          (clean)

1 of 8. The guard exists and every sibling applies it.

`.closed` IS THE ROOT; THE REST INHERIT IT
------------------------------------------
Sweeping the whole surface of an uninitialized BufferedRWPair separates the two groups
cleanly:

    SIGSEGV       .closed  iter()  list()  for-loop  .readlines()  .__enter__()  .isatty()
    ValueError    next()  .readable()  .writable()  .close()  .read()  .readline()
                  .write()  .flush()  .peek()

Everything in the first group consults `.closed` on the way in -- iteration, `readlines`,
and `__enter__` all check it first -- so a single unguarded property accounts for all seven.
The nine methods that check the underlying object directly all raise properly. That makes
this a one-line-shaped bug rather than a scattered family.

CPython has no equivalent. Measured on 3.14, the same uninitialized BufferedRWPair gives

    .closed    RuntimeError: the BufferedRWPair object is being garbage-collected
    iter()     RuntimeError (same)
    .isatty()  ValueError

-- a different exception type from PyPy's siblings, but an exception either way, never a
fault.

FOUND BY --new-uninit
---------------------
This is the RustPython "Class E" shape (a slot reading an uninitialized payload) applied to
PyPy. The fleet config predicted RPython's type safety would make a segfault *less* likely
here than on RustPython; that turned out to be wrong, and this mode is the highest-yield
variant run against PyPy so far -- 27 of 42 kept dirs in `fusil-pypy311_fleet_07`, from only
5145 sessions.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64).
"""

import re
import subprocess
import sys

_ANSI = re.compile(r"\x1b\[[0-9;]*m")

TYPES = [
    "BufferedRWPair", "BufferedRandom", "BufferedReader", "BufferedWriter",
    "TextIOWrapper", "FileIO", "BytesIO", "StringIO",
]
PROBES = [(".closed", "o.closed"), ("iter()", "iter(o)"), (".isatty()", "o.isatty()")]

SURFACE = [
    ("o.closed", "the root"), ("iter(o)", "consults .closed"),
    ("list(o)", "consults .closed"), ("[x for x in o]", "consults .closed"),
    ("o.readlines()", "consults .closed"), ("o.__enter__()", "consults .closed"),
    ("o.isatty()", "consults .closed"),
    ("next(o)", "checks directly"), ("o.readable()", "checks directly"),
    ("o.writable()", "checks directly"), ("o.close()", "checks directly"),
    ("o.read()", "checks directly"), ("o.readline()", "checks directly"),
    ("o.write(b'')", "checks directly"), ("o.flush()", "checks directly"),
    ("o.peek()", "checks directly"),
]


def probe(type_name, expr):
    code = "import _io\nT = _io.%s\no = T.__new__(T)\n%s\n" % (type_name, expr)
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, stdin=subprocess.DEVNULL,
    )
    if proc.returncode == -11:
        return "SIGSEGV"
    if proc.returncode == 0:
        return "clean"
    text = _ANSI.sub("", (proc.stdout + proc.stderr).decode("utf-8", "replace"))
    out = text.strip().splitlines()
    return out[-1].split(":")[0][:24] if out else "raises"


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))

    header = "%-18s %s" % ("type", "  ".join("%-24s" % label for label, _ in PROBES))
    print(header)
    print("-" * len(header))
    faults = 0
    for name in TYPES:
        cells = []
        for _, expr in PROBES:
            got = probe(name, expr)
            faults += got == "SIGSEGV"
            cells.append("%-24s" % got)
        print("%-18s %s" % (name, "  ".join(cells)))

    print("\nBufferedRWPair, full surface:\n")
    for expr, why in SURFACE:
        print("  %-18s %-18s %s" % (expr, probe("BufferedRWPair", expr), why))

    print()
    if faults:
        print("%d faulting cell(s). Every sibling type answers the same state with\n"
              "ValueError: I/O operation on uninitialized object." % faults)
        return 1
    print("No faults; this build guards BufferedRWPair like its siblings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
