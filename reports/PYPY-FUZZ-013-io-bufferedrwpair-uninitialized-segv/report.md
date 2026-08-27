# PYPY-FUZZ-013 — An uninitialized `_io.BufferedRWPair` segfaults through `.closed`, where every sibling type raises

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | _not pinned — see below_ |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_07 (--new-uninit variant) |
| **Defect class** | `missing-sibling-guard` |
| **Reduced from** | 27 fleet dirs, all one signature -> 1 line |
| **CPython** | PyPy-only. RuntimeError: the BufferedRWPair object is being garbage-collected |

## Reproducer

```python
import _io; _io.BufferedRWPair.__new__(_io.BufferedRWPair).closed
```

PyPy surfaces this as:

```
Segmentation fault
```

## Analysis

`T.__new__(T)` builds an instance without running `__init__`, which is ordinary Python and what pickle, copy and most deserializers do. Every other type in the family answers that state with `ValueError: I/O operation on uninitialized object` -- BufferedRandom, BufferedReader, BufferedWriter and TextIOWrapper all do. 1 of 8. `.closed` is the SINGLE ROOT: sweeping the full surface splits it cleanly, with the seven faulting operations (`.closed`, `iter()`, `list()`, for-loop, `.readlines()`, `.__enter__()`, `.isatty()`) all consulting `.closed` on the way in, while the nine that check the underlying object directly all raise properly. That makes it a one-line-shaped fix rather than a scattered family.

## Prior art

Unreported. Adjacent to two closed issues by this project's author -- pypy#5140 (StringIO segfault after an invalid `__init__` reinitialization) and pypy#5126 (StringIO in an invalid state) -- which are the SAME defect class on a different type. Both re-tested 2026-08-27 on 7.3.23: both FIXED. The fix did not propagate to BufferedRWPair.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
