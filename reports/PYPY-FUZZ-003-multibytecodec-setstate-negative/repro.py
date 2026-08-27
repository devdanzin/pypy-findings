"""PyPy 3.11 (7.3.23): a negative setstate() leaks an RPython-internal exception.

    $ pypy3.11 repro.py

Every CJK/multibyte *incremental encoder* (and the StreamWriter that wraps one) accepts an
arbitrary integer in setstate() and hands it straight to rbigint.tobytes(). A negative value
makes tobytes() raise the RPython-level InvalidSignednessError, which is not caught, so it
escapes to app level as:

    SystemError: unexpected internal exception (please report a bug):
                 <InvalidSignednessError object at 0x...>;
                 internal traceback was dumped to stderr

...with an RPython traceback dumped to stderr, ending in:

    File "pypy_module__multibytecodec.c", line 4608, in MultibyteIncrementalEncoder_setstate_w
    File "rpython_rlib.c", line 8326, in rbigint_tobytes

CPython raises a clean, documented OverflowError for the same input:

    OverflowError: can't convert negative int to unsigned

Scope: all 12 multibyte encoders (big5, cp932, cp949, euc_jp, euc_kr, gb18030, gb2312, hz,
iso2022_jp, johab, shift_jis, shift_jisx0213), via both IncrementalEncoder and StreamWriter.
The *decoders* take a tuple state and are unaffected. rbigint.tobytes is correctly guarded
elsewhere -- int.to_bytes() raises OverflowError properly -- so this is the one unvalidated
caller, not a general rbigint problem.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64).
Not the same as pypy#5010, which was about *adding* setstate/getstate; this is a missing
argument check inside that implementation.
"""

import codecs
import io
import sys

CODECS = (
    "big5", "cp932", "cp949", "euc_jp", "euc_kr", "gb18030",
    "gb2312", "hz", "iso2022_jp", "johab", "shift_jis", "shift_jisx0213",
)


def outcome(fn):
    try:
        fn()
        return "ok (no exception)"
    except SystemError as exc:
        if "report a bug" in str(exc):
            return "RPYTHON LEAK -> SystemError: %s" % str(exc)[:60]
        return "SystemError: %s" % exc
    except Exception as exc:
        return "%s: %s" % (type(exc).__name__, exc)


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))

    print("\n-- minimal case --")
    print("  codecs.getincrementalencoder('cp949')().setstate(-1)")
    print("    ->", outcome(lambda: codecs.getincrementalencoder("cp949")().setstate(-1)))

    print("\n-- every multibyte encoder --")
    leaked = []
    for name in CODECS:
        result = outcome(lambda n=name: codecs.getincrementalencoder(n)().setstate(-1))
        if result.startswith("RPYTHON LEAK"):
            leaked.append(name)
        print("  %-16s %s" % (name, result))

    print("\n-- StreamWriter (wraps the same encoder) --")
    print("  cp949 ->", outcome(
        lambda: codecs.getwriter("cp949")(io.BytesIO()).setstate(-1)))

    print("\n-- decoders (tuple state) are unaffected --")
    print("  cp949 ->", outcome(
        lambda: codecs.getincrementaldecoder("cp949")().setstate((-1, 0))))

    print("\n-- rbigint.tobytes is guarded elsewhere --")
    print("  (-1).to_bytes(4, 'little') ->", outcome(lambda: (-1).to_bytes(4, "little")))

    print("\n%d/%d encoders leak the RPython exception" % (len(leaked), len(CODECS)))
    return 1 if leaked else 0


if __name__ == "__main__":
    sys.exit(main())
