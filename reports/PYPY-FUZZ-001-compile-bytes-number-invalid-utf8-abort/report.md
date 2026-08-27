# PYPY-FUZZ-001 — `compile()` of bytes source aborts the interpreter when a digit is followed by an invalid UTF-8 byte

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | process abort |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | `pypy_interpreter_pyparser.c:25296 (_maybe_raise_number_error)`, `pypy_interpreter_pyparser.c:30295 (raise_invalid_unicode_char)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_02/03 (broad stdlib) |
| **Defect class** | `out-of-range-codepoint-from-invalid-utf8` |
| **Reduced from** | 12742-line generated script (cProfile.runctx) -> 2 bytes |
| **CPython** | PyPy-only. raises a clean SyntaxError |

## Reproducer

```python
compile(b"0\x80", "<s>", "exec")
```

PyPy surfaces this as:

```
Fatal RPython error: AssertionError
```

## Analysis

A source given as BYTES whose first token is a NUMBER, immediately followed by a byte that cannot begin a valid UTF-8 sequence. Both halves are required: `b"a\x80"` and `b"\x80"` both raise cleanly. Measured exhaustively over all 256 values of the byte after a digit, the outcome splits exactly along the UTF-8 validity classes: 0x80-0xC1 plus 0xE0 and 0xF0 abort, 0xF5-0xFF leak a KeyError (PYPY-FUZZ-008), everything else raises SyntaxError. Reaches every compilation entry point that accepts bytes -- compile(), exec(), eval() -- so any program that compiles untrusted bytes can be aborted by a 2-byte input. It cannot be caught: it is a hard abort, not an exception.

## Prior art

Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-001. An RPython AssertionError escaping generate_tokens is a recurring class -- pypy#4002 and pypy#5076 (trailing backslash, fixed in #5708) are earlier instances; the #5076 trigger no longer crashes on 7.3.23. This trigger is different: it goes through the NUMBER error path, which those did not.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
