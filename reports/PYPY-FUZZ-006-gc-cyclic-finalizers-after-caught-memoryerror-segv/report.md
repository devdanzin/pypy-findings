# PYPY-FUZZ-006 — Collecting cyclic finalizable objects after a CAUGHT `MemoryError` segfaults instead of raising

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | 4/4 at a 3072 MiB cap in the shipped 5-cap sweep; 6/6 in a separate 6-run measurement. CPython 0/20 across the same five caps |
| **Needs an address-space limit** | yes — needs the child address-space limit (`--child-memory-limit-mb`) |
| **Site(s)** | _not pinned — see below_ |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_03 (broad stdlib) |
| **Defect class** | `crash-instead-of-clean-failure-at-allocation-limit` |
| **Reduced from** | 22125-line generated script -> 14 lines |
| **CPython** | PyPy-only. exits cleanly, 20/20 across five address-space caps |

## Reproducer

```python
see repro.py -- fill the heap with cyclic __del__ objects, catch MemoryError, then gc.collect()
```

PyPy surfaces this as:

```
Segmentation fault (and NOT PyPy's clean "out of memory: couldn't allocate the next arena" abort, whose absence is what distinguishes this from mere exhaustion)
```

## Analysis

The MemoryError is caught, so at that point the program is in a state Python defines as recoverable; collecting the cycles then crashes instead of raising. Every line of the 14 is load-bearing, measured 4 runs each: without `__del__` 0/4, without the reference cycle 0/4, without the gc.collect() loop 0/4, and -- the interesting one -- without an `import weakref` that is NEVER USED, 0/4. Substituting bytearrays, 20000 objects, 20000 dicts or `import functools` for that import does not restore it, so the threshold is in the GC heap's SHAPE, not its size. The shipped reproducer therefore SWEEPS a range of caps instead of hardcoding one.

## Prior art

Unreported. NOT seeded in the toolkit catalog: it was added to the findings report after the five-bug version was handed over.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
