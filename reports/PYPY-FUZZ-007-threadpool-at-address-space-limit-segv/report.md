# PYPY-FUZZ-007 — `multiprocessing.pool.ThreadPool()` segfaults when worker-thread creation starts failing

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | sweeps; 6-7/10 at the right ballast, 0/10 one step either side |
| **Needs an address-space limit** | yes — needs the child address-space limit (`--child-memory-limit-mb`) |
| **Site(s)** | `lib/pypy3.11/multiprocessing/pool.py:314 (_repopulate_pool_static)`, `lib/pypy3.11/multiprocessing/pool.py:183 (Pool.__init__)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_03 (broad stdlib) |
| **Defect class** | `crash-instead-of-clean-failure-at-allocation-limit` |
| **Reduced from** | 22249-line generated script -> 4 lines |
| **CPython** | PyPy-only. raises cleanly under an identical limit and ballast (0/10) |

## Reproducer

```python
see repro.py -- allocate ballast under RLIMIT_AS, then ThreadPool()
```

PyPy surfaces this as:

```
Fatal Python error: Segmentation fault, in _repopulate_pool_static
```

## Analysis

The benign outcome, which PyPy produces most of the time and is presumably the intended one, is `AttributeError: 'DummyProcess' object has no attribute 'terminate'` from Pool.__init__'s own cleanup path. The bug is that the same situation sometimes segfaults instead. The crash needs the process in a narrow band below the limit -- enough address space to start the pool, not enough to finish -- and the band moves between machines AND between edits of the reproducer file itself: adding a docstring moved it by 150 MiB. A self-calibrating variant (fill, then release fixed headroom) does NOT reproduce it, so the ballast is not merely a proxy for 'nearly full'. Hence the sweep.

## Prior art

Unreported. NOT seeded in the toolkit catalog (added to the report after hand-over). The single highest-volume signature of the whole campaign: 13 of 58 kept dirs in one fleet and 5 in another, across every instance.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
