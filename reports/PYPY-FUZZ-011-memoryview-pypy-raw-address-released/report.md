# PYPY-FUZZ-011 — `memoryview._pypy_raw_address()` dereferences a RELEASED view where every sibling member raises

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
| **Found by** | fusil, fleet_06 (broad stdlib, --test-private) |
| **Defect class** | `missing-sibling-guard` |
| **Reduced from** | fleet dirs -> 3 lines |
| **CPython** | PyPy-only. no such method -- `_pypy_raw_address` is PyPy-only |

## Reproducer

```python
m = memoryview(b""); m.release(); m._pypy_raw_address()
```

PyPy surfaces this as:

```
Segmentation fault
```

## Analysis

Measured over the whole public surface of `memoryview` on a released view, one member per subprocess: 14 members raise `ValueError: operation forbidden on released memoryview object`, 3 (`c_contiguous`, `contiguous`, `f_contiguous`) return a value without checking, and exactly one faults -- the one whose entire job is to hand back a raw pointer into the buffer. 1 of 19. Reachable from idiomatic code, not only an explicit `.release()`: `memoryview` is a context manager and `__exit__` releases, so the ordinary `with` form crashes identically. There is no CPython differential to offer, so the argument is internal consistency -- which is the stronger one: PyPy already decided what should happen here, implemented it 14 times, and missed the 15th.

## Prior art

Unreported; no tracker issue mentions `_pypy_raw_address`. NOTE ON METHOD: an earlier keyword search reported 'no prior art' for several findings in this catalog and was wrong, because the relevant closed issues name different TYPES in their titles. This particular claim was re-checked directly.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
