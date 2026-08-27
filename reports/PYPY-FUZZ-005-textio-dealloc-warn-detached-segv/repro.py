"""PyPy 3.11 (7.3.23): _dealloc_warn() on a DETACHED TextIOWrapper still segfaults.

    $ pypy3.11 repro.py        # -> SIGSEGV

This is an INCOMPLETE FIX of pypy#5123, not a new bug.

#5123 ("Calling `_dealloc_warn` on a detached `TextIOWrapper` segfaults", devdanzin,
2024-11-15) was closed the next day by mattip: "Fixed in 7bc330cce0f". That commit added the
missing guard to **pypy/module/_io/interp_bufferedio.py**:

    def _dealloc_warn_w(self, space, w_source):
        if self.w_raw:
            space.call_method(self.w_raw, "_dealloc_warn", w_source)
        else:
            raise oefmt(space.w_RuntimeError,
                 "calling _dealloc_warn' on a closed or detached reader")

...i.e. it guarded the BUFFERED layer's `w_raw`. The TEXT layer, in
**pypy/module/_io/interp_textio.py**, holds its buffer as `w_buffer` and was not touched, so
TextIOWrapper._dealloc_warn still dereferences a detached buffer. Verified on 7.3.23:

    BufferedReader  -> RuntimeError: calling _dealloc_warn' on a closed or detached reader
    BufferedWriter  -> RuntimeError  (same)
    BufferedRandom  -> RuntimeError  (same)
    TextIOWrapper   -> SIGSEGV                                <-- still unguarded

The asymmetry inside TextIOWrapper itself makes the intended behaviour obvious: every other
method on a detached wrapper raises cleanly, and only this one crashes.

    read/write/flush/fileno/seek/close  -> ValueError: underlying buffer has been detached
    _dealloc_warn                       -> SIGSEGV

Conditions: the wrapper must be DETACHED (merely closed is handled correctly) and one
argument must be passed; its value is irrelevant (None, an int and object() all crash).
CPython does not expose _dealloc_warn on TextIOWrapper at all, so there is no CPython
counterpart to compare against.

Suggested fix: mirror the 7bc330cce0f guard in interp_textio.py's _dealloc_warn_w, checking
`w_buffer` -- or simply route it through the same _check_attached() that read/write/flush use,
which would give the ValueError the sibling methods already produce.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64), via sys.__stdin__.
"""

import io
import sys


def show(label, fn):
    try:
        fn()
        return "%-34s -> no error" % label
    except Exception as exc:
        return "%-34s -> %s: %s" % (label, type(exc).__name__, exc)


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))

    print("\n-- the buffered layer, guarded by 7bc330cce0f --")
    for name, make in (
        ("BufferedReader", lambda: io.BufferedReader(io.BytesIO(b"x"))),
        ("BufferedWriter", lambda: io.BufferedWriter(io.BytesIO())),
        ("BufferedRandom", lambda: io.BufferedRandom(io.BytesIO(b"x"))),
    ):
        obj = make()
        obj.detach()
        print("  " + show(name, lambda o=obj: o._dealloc_warn(object())))

    print("\n-- every other TextIOWrapper method guards the detached buffer --")
    for name, call in (
        ("read", lambda w: w.read()),
        ("write", lambda w: w.write("x")),
        ("flush", lambda w: w.flush()),
        ("fileno", lambda w: w.fileno()),
        ("seek", lambda w: w.seek(0)),
        ("close", lambda w: w.close()),
    ):
        wrapper = io.TextIOWrapper(io.BytesIO(b"x"))
        wrapper.detach()
        print("  " + show(name, lambda w=wrapper, c=call: c(w)))

    print("\n-- merely CLOSED (not detached) is handled correctly too --")
    wrapper = io.TextIOWrapper(io.BytesIO(b"x"))
    wrapper.close()
    print("  " + show("_dealloc_warn after close", lambda: wrapper._dealloc_warn(object())))

    print("\n-- DETACHED: the one unguarded path --")
    wrapper = io.TextIOWrapper(io.BytesIO(b"x"))
    wrapper.detach()
    print("  calling wrapper._dealloc_warn(None) now; expect SIGSEGV ...", flush=True)
    wrapper._dealloc_warn(None)
    print("  !! survived -- the guard is present, this PyPy is fixed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
