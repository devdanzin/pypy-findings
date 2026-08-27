"""PyPy 3.11 (7.3.23): compiling BYTES crashes the tokenizer's number-error path, two ways.

    $ pypy3.11 repro.py

One function -- `_maybe_raise_number_error` in PyPy's PEG tokenizer -- mishandles the
byte that follows a numeric literal when the source is given as BYTES rather than str.
Depending on which invalid byte follows, it fails in one of two different ways:

  A. HARD ABORT (uncatchable), 2 bytes:

        $ pypy3.11 -c 'compile(b"0\x80", "<s>", "exec")'
        RPython traceback:
          File "pypy_interpreter_pyparser.c", line 3756, in PegParser__parse
          File "pypy_interpreter_pyparser.c", line 16487, in generate_tokens
          File "pypy_interpreter_pyparser.c", line 25296, in _maybe_raise_number_error
          File "pypy_interpreter_pyparser.c", line 30295, in raise_invalid_unicode_char
        Fatal RPython error: AssertionError
        Aborted (core dumped)

  B. RPython-EXCEPTION LEAK, 4 bytes:

        $ pypy3.11 -c 'compile(b"0\xf5aa", "<s>", "exec")'
        RPython traceback:
          ... same four frames ...
          File "pypy_interpreter_pyparser.c", line 24992, in _maybe_raise_number_error
          File "rpython_rlib_unicodedata.c", line 542, in _db_index
        SystemError: unexpected internal exception (please report a bug):
                     <KeyError object at 0x...>; internal traceback was dumped to stderr

     An RPython-internal KeyError escapes to application level as SystemError. The process
     survives, but the exception is meaningless to the caller and the message asks the user
     to report a bug.

CPython raises a clean SyntaxError for every input below.

WHICH BYTE DOES WHAT
--------------------
Measured exhaustively over all 256 values of the byte following a digit (padding with
enough trailing bytes for each case):

    0x80 - 0xC1   ABORT           continuation bytes + the overlong 2-byte leads
    0xE0, 0xF0    ABORT           the overlong-capable 3- and 4-byte leads
    0xF5 - 0xFF   SystemError     leads that could only encode a codepoint > U+10FFFF
    everything else               clean SyntaxError

The split lines up with the UTF-8 validity classes, which is what makes it look like one
root cause with two faces: a byte that cannot begin a valid sequence produces an out-of-range
"codepoint", and the error path then either asserts on it (A) or hands it to the unicodedata
table, which raises KeyError (B).

BOTH halves of the trigger are required. The literal is what routes through
`_maybe_raise_number_error`:

    compile(b"0\x80",   ...) -> ABORT         digit + invalid byte
    compile(b"7\xc1",   ...) -> ABORT         any digit, any qualifying byte
    compile(b"0\xf5aa", ...) -> SystemError   digit + out-of-range lead + 2 bytes
    compile(b"a\x80",   ...) -> SyntaxError   not a number -> different error path
    compile(b"\x80",    ...) -> SyntaxError   no number
    compile(b"0\xf5",   ...) -> SyntaxError   too short to form the bad codepoint

Face B needs two more bytes after the lead byte; with fewer, the decoder hits end-of-input
first and reports a clean SyntaxError. That is why the 2-byte probe `b"0\xff"` -- the
negative control in the first version of this file -- looked harmless.

Both faces reach every compilation entry point that accepts bytes: compile(), exec(),
eval(), and bytearray sources. Any program that compiles or execs untrusted bytes can be
aborted by a 2-byte input. Face A cannot be caught: it is a hard abort, not an exception.

CONTEXT: an RPython AssertionError escaping from generate_tokens is a recurring class in
PyPy's PEG parser -- pypy#4002 and pypy#5076 (trailing backslash, fixed in #5708) are
earlier instances, and the #5076 trigger no longer crashes on 7.3.23. This trigger is
different: it goes through the NUMBER error path, which those did not. Both faces are
unreported.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64). Face A came from
cProfile.runctx() exec'ing a fuzzer-chosen bytes object (12742-line generated script ->
2 bytes); face B from code.InteractiveConsole.runcode() doing the same
(12805 lines -> 4 bytes, b"2\xff*\x17", then simplified to b"0\xf5aa").
"""

import subprocess
import sys

ABORT, LEAK, CLEAN = "ABORT", "SystemError leak", "clean SyntaxError"

CASES = [
    (b"0\x80",     "digit + continuation byte",          ABORT),
    (b"7\xc1",     "another digit, another lead byte",   ABORT),
    (b"1\xe0a",    "overlong-capable 3-byte lead",       ABORT),
    (b"0\xf5aa",   "digit + out-of-range lead + 2 bytes", LEAK),
    (b"9\xffzz",   "another digit, another lead",         LEAK),
    (b"0\xf5",     "same lead, too short",                CLEAN),
    (b"0\xe9aa",   "valid 3-byte lead",                   CLEAN),
    (b"a\x80",     "letter instead of a digit",           CLEAN),
    (b"\x80",      "no number",                           CLEAN),
]

MODES = ["compile", "exec", "eval"]


def probe(source, mode):
    """Run one compilation in a fresh interpreter; return (returncode, output)."""
    if mode == "compile":
        call = "compile(%r, '<s>', 'exec')" % (source,)
    else:
        call = "%s(%r)" % (mode, source)
    # Swallow SyntaxError in the child so that a clean rejection exits 0 and only a real
    # crash produces a non-zero status.
    code = "try:\n %s\nexcept SyntaxError as e:\n print('SyntaxError:', e)\n" % call
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    return proc.returncode, (proc.stdout + proc.stderr).decode("utf-8", "replace")


def classify(returncode, output):
    if "Fatal RPython error" in output:
        return ABORT
    if "SystemError" in output and "KeyError" in output:
        return LEAK
    if "SyntaxError" in output:
        return CLEAN
    return "unexpected(rc=%d)" % returncode


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    print()
    header = "%-14s %-36s %-18s %s" % ("source", "why", "expected", "  ".join(
        "%-17s" % m for m in MODES))
    print(header)
    print("-" * len(header))

    failures = 0
    for source, why, expected in CASES:
        cells = []
        for mode in MODES:
            got = classify(*probe(source, mode))
            cells.append("%-17s" % got)
            if got != expected:
                failures += 1
        print("%-14s %-36s %-18s %s" % (repr(source), why, expected, "  ".join(cells)))

    print()
    if failures:
        print("%d cell(s) did not match the expected outcome -- this build differs from\n"
              "PyPy 7.3.23, or the bug is fixed." % failures)
        return 1
    print("All outcomes as documented. On CPython every cell reads 'clean SyntaxError'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
