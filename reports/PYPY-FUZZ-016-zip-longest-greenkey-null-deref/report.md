# PYPY-FUZZ-016 — A spent `zip_longest` segfaults any bulk consumer -- `list`, `set`, `sorted`, `min`, `[*z]`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | 12/12 single runs, no threads, no timing dependence (CPython 3.14.3: 0/12) |
| **Needs an address-space limit** | no |
| **Site(s)** | `pypy/module/itertools/interp_itertools.py:681 (W_ZipLongest.iterator_greenkey, the unguarded read)`, `pypy/module/itertools/interp_itertools.py:642 (W_ZipLongest._fetch, the write that puts None there)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_08 (--concurrency-stress variant), 2 dirs of 229 |
| **Defect class** | `copied-invariant-broken-in-the-copy` |
| **Reduced from** | 1745-line generated script -> 3 lines |
| **CPython** | PyPy-only. returns [] -- a spent zip_longest is simply empty |

## Reproducer

```python
import itertools
z = itertools.zip_longest([], [1, 2, 3])
next(z)   # arg 0 is exhausted here; z itself is still live
list(z)   # SIGSEGV
```

PyPy surfaces this as:

```
Segmentation fault
```

## Analysis

`W_ZipLongest._fetch` stores None into `self.iterators_w[i]` when sub-iterator i raises StopIteration while others are still active (interp_itertools.py:642). `W_ZipLongest.iterator_greenkey` then reads `self.iterators_w[0]` and calls a method on it with no None check (line 681), which in translated RPython is a call through a null pointer. `iterator_greenkey` is consulted by the space-level BULK UNPACK path -- `_do_extend_from_iterable` and its set/dict/unicode counterparts -- so it fires for list(), tuple(), set(), frozenset(), dict(), sorted(), min(), list.extend() and [*z], and NOT for a `for` loop, a bare next(), a list comprehension or a generator expression, which go through FOR_ITER instead. That split is the whole diagnosis and it was measured, 16 consumers. The mechanism predicts exactly when it fires, and all seven predictions hold: it needs the FIRST argument to be among the first exhausted, because only then is index 0 the one nulled. zip_longest([1,2,3], range(10)) faults; zip_longest(range(10), [1,2,3]) does not (arg 0 outlives the others, and when `active` finally hits 0 the raise happens BEFORE the assignment); equal lengths fault; a single argument does not (`active` goes 1 -> 0, so the raise pre-empts the nulling); zero arguments do not (len(iterators_w) == 0 short-circuits). It is a copied invariant, not a forgotten guard. The identical method body -- down to the same `XXX in theory we should tupleize` comment -- also sits on W_Map and W_Zip in pypy/module/__builtin__/functional.py, where it is correct, because neither ever stores None into iterators_w; both were verified clean on the same double-consume. `W_ZipLongest.iterator_greenkey` was copied to this class by 6bd66bda3c ('make W_ZipLongest stop subclassing from W_Map as well', 2022-06-11), long after the nulling it invalidates, which has been in `_fetch` since izip_longest was first implemented. The class already knows the entry can be None: `descr_reduce` writes `iterator if iterator is not None else space.newtuple([])` a dozen lines above. By git history the read has been reachable since release-pypy3.9-v7.3.10 (28 release tags); only 7.3.23 was tested. It is live on main: interp_itertools.py is byte-identical between the 7.3.23 tag and fe2af5843a (2026-08-18) apart from an unrelated `tee` change, and the rest of the call path is untouched too -- objspace/std/listobject.py and setobject.py have no diff at all, and baseobjspace.py's diff contains no greenkey line. Fix is a None check at the read, matching what descr_reduce already does.

## Prior art

Unreported. The tracker has no issue mentioning `iterator_greenkey` and only one unrelated 2014 performance issue (#2104) mentioning zip_longest. Not adjacent to any closed issue in this catalog's set.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
