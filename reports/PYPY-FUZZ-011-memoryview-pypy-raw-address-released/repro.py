"""PyPy 3.11 (7.3.23): memoryview._pypy_raw_address() on a RELEASED view segfaults.

    $ pypy3.11 repro.py

    $ pypy3.11 -c 'm = memoryview(b""); m.release(); m._pypy_raw_address()'
    Segmentation fault (core dumped)

Three lines, no arguments, no memory pressure, no threads. Deterministic.

`.release()` invalidates the view; every other member of `memoryview` knows that and says so:

    ValueError: operation forbidden on released memoryview object

`_pypy_raw_address` is the one member that skips the check -- and it is the member whose whole
job is to hand back a raw pointer into the buffer. Measured over the full public surface of
`memoryview` on a released view, one member at a time in its own subprocess:

    _pypy_raw_address                              SIGSEGV
    cast format hex itemsize nbytes ndim obj       ValueError, as documented
    readonly shape strides suboffsets tobytes
    tolist toreadonly
    c_contiguous contiguous f_contiguous           return a value without checking
                                                   (inconsistent, but harmless)

1 of 19. So this is not "the API lets you shoot yourself" -- the guard exists, is applied
consistently everywhere else, and is simply missing here.

REACHABLE FROM IDIOMATIC CODE
-----------------------------
It is not only the explicit `.release()` call. `memoryview` is a context manager and
`__exit__` releases, so the ordinary `with` form crashes identically:

    with memoryview(bytearray(b"abc")) as m:
        pass
    m._pypy_raw_address()        # SIGSEGV

A slice taken before the parent is released keeps its own reference and still works, so the
bug is specifically use-after-release of the view you called it on.

NO CPYTHON DIFFERENTIAL EXISTS
------------------------------
`_pypy_raw_address` is PyPy-only; CPython has no such method, so there is nothing to compare
against. The argument here is internal consistency instead, which is the stronger one: PyPy
already decided what should happen when a released view is used, implemented it 14 times, and
missed the 15th.

SAME SHAPE AS AN EARLIER FINDING
--------------------------------
This is structurally identical to the `TextIOWrapper._dealloc_warn` crash in the same
campaign: a private, easily-overlooked method that skips the invalidation guard its public
siblings all apply, and dereferences the stale pointer. Both were found by fuzzing private
members (`--test-private`), which is why that flag is load-bearing in the fleet config.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64), in two independent fleet
instances (`fusil-pypy311_fleet_06`, `inst-01` and `inst-02`, both labelled
`builtins-segmentation_fault`).
"""

import subprocess
import sys

CASES = [
    ("explicit release",
     'm = memoryview(bytearray(b"abc")); m.release(); m._pypy_raw_address()', True),
    ("release of an empty view",
     'm = memoryview(b""); m.release(); m._pypy_raw_address()', True),
    ("released via `with` (idiomatic)",
     'm = memoryview(bytearray(b"abc"))\nwith m: pass\nm._pypy_raw_address()', True),
    ("released array view",
     'import array\nm = memoryview(array.array("i", [1, 2]))\nm.release()\n'
     'm._pypy_raw_address()', True),
    ("live view (control)",
     'memoryview(bytearray(b"abc"))._pypy_raw_address()', False),
    ("live slice of a released parent (control)",
     'b = bytearray(b"abcdef")\nm = memoryview(b)\ns = m[1:3]\nm.release()\n'
     's._pypy_raw_address()', False),
    ("another member on a released view (control)",
     'm = memoryview(bytearray(b"abc")); m.release(); m.tobytes()', False),
]


def run(code):
    """Run one snippet in a fresh interpreter; return (crashed, detail)."""
    wrapped = (
        "try:\n"
        "    exec(%r)\n"
        "except Exception as e:\n"
        "    print(type(e).__name__ + ': ' + str(e)[:60])\n" % code
    )
    proc = subprocess.run(
        [sys.executable, "-c", wrapped],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    if proc.returncode == -11:
        return True, "SIGSEGV"
    if proc.returncode != 0:
        return True, "died rc=%d" % proc.returncode
    out = (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()
    return False, out.splitlines()[-1][:52] if out else "no error"


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    if not hasattr(memoryview, "_pypy_raw_address"):
        print("memoryview._pypy_raw_address does not exist on this interpreter "
              "(it is PyPy-only); nothing to test.")
        return 0

    unexpected = 0
    for label, code, should_crash in CASES:
        crashed, detail = run(code)
        mark = "  " if crashed == should_crash else "??"
        if crashed != should_crash:
            unexpected += 1
        print("%s %-42s %s" % (mark, label, detail))

    print()
    if unexpected:
        print("%d case(s) behaved unexpectedly -- this build differs from PyPy 7.3.23,\n"
              "or the guard has been added." % unexpected)
        return 1
    print("All cases as documented: _pypy_raw_address is the only memoryview member that\n"
          "dereferences a released view instead of raising ValueError.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
