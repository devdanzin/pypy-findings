# PYPY-FUZZ-002 — `struct.unpack('u', ...)` passes an unvalidated 4-byte codepoint to `rutf8.unichr_as_utf8`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SystemError leak |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | `pypy_module_struct.c:4652 (UnpackFormatIterator_append_utf8)`, `rpython_rlib.c:10474 (unichr_as_utf8)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_02 (broad stdlib) |
| **Defect class** | `unvalidated-rpython-helper-call` |
| **Reduced from** | 22242-line generated script -> 1 line |
| **CPython** | PyPy-only. the 'u' format was removed in 3.9; struct.error |

## Reproducer

```python
import struct; struct.unpack("u", b"abcd")
```

PyPy surfaces this as:

```
SystemError: unexpected internal exception (please report a bug): <OutOfRange object ...>
```

## Analysis

The 'u' unpack format reads four bytes and hands them to `rutf8.unichr_as_utf8` as a codepoint with no range check at all, so any four bytes decoding above U+10FFFF raise RPython's `OutOfRange`, which nothing in the struct module catches. One line, no state, no timing.

## Prior art

Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-002. The static catalog's PYPYR-0004 notes this as the same shape with the range check ABSENT, where PYPYR-0004 has the range check present and the surrogate clause absent.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
