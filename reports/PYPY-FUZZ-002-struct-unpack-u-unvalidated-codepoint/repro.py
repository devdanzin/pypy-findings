"""PyPy 3.11 (7.3.23): struct.unpack("u", ...) leaks an RPython-internal exception.

    $ pypy3.11 -c 'import struct; struct.unpack("u", b"abcd")'
    SystemError: unexpected internal exception (please report a bug):
                 <OutOfRange object at 0x...>; internal traceback was dumped to stderr

    RPython traceback:
      File "pypy_module_struct.c", line 4652, in UnpackFormatIterator_append_utf8
      File "rpython_rlib.c", line 11352, in unichr_as_utf8

CPython raises a clean `struct.error: bad char in struct format` -- it REMOVED the legacy
'u' (UCS-4 character) format in 3.9. PyPy still accepts it, reads four bytes as a codepoint,
and hands that straight to `unichr_as_utf8` without validating it. Any value outside the
Unicode range, and any surrogate, escapes as an RPython-level OutOfRange:

    U+10FFFF   -> ok, ('\U0010ffff',)      the last valid codepoint
    U+110000   -> RPython leak             first value above the range
    U+FFFFFFFF -> RPython leak
    U+D800     -> RPython leak             surrogates are rejected by unichr_as_utf8 too

b"abcd" is simply 0x64636261 little-endian = 1684234849, far above U+10FFFF, which is why
the one-liner above is enough.

The result is not a crash, but the message says "please report a bug" because an
RPython-level exception was never meant to reach application level: the interpreter cannot
say what went wrong, and no `except struct.error` will catch it.

Related class, different site: pypy#3047 ("Internal exception when loading json with unicode
escapes"). No prior report for the struct 'u' path.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64). Reduced from a 22242-line
generated zipfile session (zipfile._EXTRA_FIELD_STRUCT is a struct.Struct) to this one call;
the original hit needed two threads racing Struct.__init__ against Struct.unpack, but the
race turned out to be incidental -- re-initialising the Struct to a 'u' format was the only
thing the second thread contributed.
"""

import struct
import sys


def describe(fn):
    try:
        return "ok %r" % (fn(),)
    except SystemError as exc:
        if "report a bug" in str(exc):
            return "RPYTHON LEAK -> SystemError: %s" % str(exc)[:58]
        return "SystemError: %s" % exc
    except Exception as exc:
        return "%s: %s" % (type(exc).__name__, exc)


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))

    print("-- the one-liner --")
    print("  struct.unpack('u', b'abcd')  ->",
          describe(lambda: struct.unpack("u", b"abcd")))

    print("\n-- it is a codepoint-range check that is missing --")
    for codepoint in (0x10FFFF, 0x110000, 0x110001, 0xFFFFFFFF, 0xD800):
        raw = struct.pack("<I", codepoint)
        print("  U+%06X ->" % codepoint, describe(lambda r=raw: struct.unpack("u", r)))

    print("\n-- CPython removed the 'u' format in 3.9 and rejects it outright --")
    print("  (there it raises struct.error: bad char in struct format)")

    leaked = "report a bug" in describe(lambda: struct.unpack("u", b"abcd"))
    return 1 if leaked else 0


if __name__ == "__main__":
    sys.exit(main())
