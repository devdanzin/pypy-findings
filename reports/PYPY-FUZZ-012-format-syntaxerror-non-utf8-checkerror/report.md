# PYPY-FUZZ-012 — Formatting a SyntaxError from non-UTF-8 source leaks an RPython `CheckError`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SystemError leak |
| **Status** | `reproduced` |
| **Reliability** | deterministic (6/6 rows on PyPy, 0/6 on CPython) |
| **Needs an address-space limit** | no |
| **Site(s)** | `implement_3.c:59620 (fastfunc_descr__format___2)`, `pypy_objspace_std_8.c:58764 (Formatter_format_string)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_06 (broad stdlib) |
| **Defect class** | `out-of-range-codepoint-from-invalid-utf8` |
| **Reduced from** | 12748-line generated script -> 752 -> 53 lines -> 2 bytes |
| **CPython** | PyPy-only. formats the same exception cleanly |

## Reproducer

```python
import traceback
try:
    compile(b"\xff", b"\x80", "exec")
except SyntaxError as e:
    traceback.format_exception(type(e), e, e.__traceback__)
```

PyPy surfaces this as:

```
SystemError: unexpected internal exception (please report a bug): <CheckError object ...>
```

## Analysis

BOTH halves must be invalid UTF-8, and the conjunction is the whole trigger: the SOURCE must be non-UTF-8 to produce the "Non-UTF-8 code starting with ..." SyntaxError, whose message embeds the filename, and the FILENAME must be non-UTF-8 for that embedding to go wrong. It is the FORMATTING that fails, not the compile -- `compile()` raises an ordinary SyntaxError and the leak happens when anything renders it (`format_exception`, `print_exception`, or `threading.excepthook` for an exception leaving a thread, which is how the fuzzer hit it). Left unhandled, the same input prints the filename as `\Uffffefa0`, which is not a codepoint: `\x80` should surrogate-escape to `\udc80`. That out-of-range value is the same producer behind PYPY-FUZZ-001 and 008, with a third consumer failing a third way -- fixing the producer would likely close all three, whereas guarding each consumer would not.

## Prior art

Unreported, but adjacent to TWO closed issues by this project's author. pypy#5111 (`_string.formatter_field_name_split(b'\xe1')`) leaked the SAME CheckError and is FIXED on 7.3.23 -- this path is a door the fix did not reach. pypy#5121 (`logging._str_formatter.vformat(b'\xff', ...)`) is also fixed. DISTINCT from the static catalog's PYPYR-0004 (`format(0xD800,'c')`), verified side by side: different RPython exception (OutOfRange vs CheckError), different guard, different entry point.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
