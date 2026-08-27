# PYPY-FUZZ-005 — `TextIOWrapper._dealloc_warn()` on a detached wrapper dereferences a null buffer

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | `pypy/module/_io/interp_textio.py:847 (per the static catalog's PYPYR-0001)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_02 (broad stdlib, --test-private) |
| **Defect class** | `missing-sibling-guard` |
| **Reduced from** | fleet dirs -> 3 lines |
| **CPython** | PyPy-only. CPython does not expose _dealloc_warn on TextIOWrapper at all |

## Reproducer

```python
import sys
sys.__stdin__.detach()
sys.__stdin__._dealloc_warn(1)
```

PyPy surfaces this as:

```
Segmentation fault
```

## Analysis

Buffered Reader/Writer/Random now raise RuntimeError after detach; TextIOWrapper still segfaults, while its own read/write/flush/fileno/seek/close all raise "underlying buffer has been detached". The guard exists on 17 sibling methods of the same class. This is the first of four findings in this catalog with that exact shape -- see PYPY-FUZZ-011, 013 and 014.

## Prior art

THIS IS AN INCOMPLETE FIX OF A CLOSED ISSUE. pypy#5123 was filed by this project's author and closed; mattip's fix (7bc330cce0f, 2024-11-16) guarded the BUFFERED layer (interp_bufferedio.py) and left the TEXT layer alone. Re-tested 2026-08-27 on 7.3.23: the original reproducer from #5123 STILL SEGFAULTS. Also seeded as PYPY-FUZZ-005 and pinned to a line by the static catalog as PYPYR-0001, with PYPYR-0002 recording a second route (`__new__` bypass) that this reproducer does not exercise.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
