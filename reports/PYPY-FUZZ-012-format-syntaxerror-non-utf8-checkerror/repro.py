"""PyPy 3.11 (7.3.23): formatting a SyntaxError from non-UTF-8 source leaks an RPython CheckError.

    $ pypy3.11 repro.py

    >>> import traceback
    >>> try:
    ...     compile(b"\\xff", b"\\x80", "exec")
    ... except SyntaxError as e:
    ...     traceback.format_exception(type(e), e, e.__traceback__)
    RPython traceback:
      File "pypy_interpreter.c", line 53929, in BuiltinCode2_fastcall_2
      File "implement_3.c", line 59620, in fastfunc_descr__format___2
      File "pypy_objspace_std_8.c", line 58764, in Formatter_format_string
    SystemError: unexpected internal exception (please report a bug):
                 <CheckError object at 0x...>; internal traceback was dumped to stderr

One byte of source, one byte of filename. An RPython-internal exception escapes to
application level as a SystemError whose text asks the user to report a bug. CPython formats
the same exception without complaint.

BOTH HALVES MUST BE INVALID UTF-8
---------------------------------
    source        filename       formatting the SyntaxError
    b"("          "f.py"         clean
    b"("          b"\\xC1\\x92\\xDF"  clean
    b"abc\\xe9\\xff"  "f.py"         clean
    b"abc\\xe9\\xff"  b"\\xC1\\x92\\xDF"  LEAK

The source must be non-UTF-8 to produce the "Non-UTF-8 code starting with ..." SyntaxError,
whose message embeds the filename; the filename must be non-UTF-8 for the embedding to go
wrong. Minimal on both sides: `compile(b"\\xff", b"\\x80", "exec")`.

It is the FORMATTING that fails, not the compile. `compile()` raises a perfectly ordinary
SyntaxError; the leak happens when something renders it -- `traceback.format_exception`,
`traceback.print_exception`, or `threading.excepthook` for an exception crossing out of a
thread, which is how fusil found it.

PROBABLY THE SAME ROOT AS THE TOKENIZER BUGS
--------------------------------------------
Left unhandled, the same input prints:

    SyntaxError: Non-UTF-8 code starting with '\\xff' in file \\Uffffefa0 on line 1, ...

`\\Uffffefa0` is not a codepoint. The filename byte `\\x80` should surrogate-escape to
`\\udc80`; instead something has produced a value far beyond U+10FFFF, and the RPython range
check in the string formatter is what finally notices.

That is the same shape as the two faces in `../pypy_compile_bytes_abort/`: an invalid UTF-8
byte in bytes source becomes an out-of-range "codepoint", and whichever consumer meets it
next fails in its own way --

    _maybe_raise_number_error -> raise_invalid_unicode_char   Fatal RPython error (abort)
    _maybe_raise_number_error -> unicodedata._db_index        KeyError  -> SystemError
    descr__format__ -> Formatter_format_string                CheckError -> SystemError

Three faces, three consumers, one apparent cause. Worth reporting together: fixing the
producer would likely close all of them, whereas guarding each consumer would not.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64), in two independent fleet
instances (`fusil-pypy311_fleet_06`, `inst-03` and `inst-06`, both
`importlib_machinery-systemerror`). The original was a 12748-line script calling
`SourceFileLoader.source_to_code(memoryview(bytearray(b"abc\\xe9\\xff")), b"\\xC1\\x92\\xDF")`
in a thread; reduced to 53 lines by `prune.py` under `predicate.py` (8/8), then by hand to
the two bytes above.
"""

import subprocess
import sys

CASES = [
    # (source, filename, expected leak)
    (b"\xff", b"\x80", True, "minimal: 1 byte each"),
    (b"abc\xe9\xff", b"\xC1\x92\xDF", True, "as found by the fuzzer"),
    (b"a\xe9", b"\xff", True, "another pair"),
    (b"(", b"\xC1\x92\xDF", False, "valid-UTF-8 source (control)"),
    (b"abc\xe9\xff", "f.py", False, "valid-UTF-8 filename (control)"),
    (b"(", "f.py", False, "both valid (control)"),
]

CHILD = """
import traceback
exc = None
try:
    compile({source!r}, {filename!r}, "exec")
except SyntaxError as e:
    exc = e
if exc is None:
    print("NO SYNTAXERROR")
else:
    try:
        traceback.format_exception(type(exc), exc, exc.__traceback__)
        print("CLEAN")
    except SystemError as ex:
        print("LEAK" if "CheckError" in str(ex) else "SYSTEMERROR")
"""


def probe(source, filename):
    proc = subprocess.run(
        [sys.executable, "-c", CHILD.format(source=source, filename=filename)],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    out = (proc.stdout + proc.stderr).decode("utf-8", "replace")
    if proc.returncode != 0:
        return "died rc=%d" % proc.returncode
    for marker in ("LEAK", "CLEAN", "NO SYNTAXERROR", "SYSTEMERROR"):
        if marker in out:
            return marker
    return "?"


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    header = "%-30s %-16s %-16s %s" % ("case", "source", "filename", "result")
    print(header)
    print("-" * len(header))

    leaks = unexpected = 0
    for source, filename, should_leak, label in CASES:
        got = probe(source, filename)
        if got == "LEAK":
            leaks += 1
        if (got == "LEAK") != should_leak:
            unexpected += 1
        print("%-30s %-16s %-16s %s" % (label, repr(source)[:16], repr(filename)[:16], got))

    print()
    if unexpected:
        print("%d case(s) differ from PyPy 7.3.23. On CPython every row reads CLEAN, which is\n"
              "the expected result there." % unexpected)
        return 1 if leaks else 0
    if leaks:
        print("An RPython-internal CheckError reached application level as SystemError.\n"
              "CPython formats every one of these exceptions cleanly.")
        return 1
    print("No leak; this build formats all of them cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
