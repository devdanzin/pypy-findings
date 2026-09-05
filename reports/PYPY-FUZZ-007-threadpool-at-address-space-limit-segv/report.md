# PYPY-FUZZ-007 — `multiprocessing.pool.ThreadPool()` segfaults when worker-thread creation starts failing

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | 6/8 at `ulimit -v 524288` with no ballast; via ballast, sweeps 6-7/10 at the right size and 0/10 one step either side |
| **Needs an address-space limit** | yes — needs the child address-space limit (`--child-memory-limit-mb`) |
| **Site(s)** | `lib/pypy3.11/multiprocessing/pool.py:314 (_repopulate_pool_static)`, `lib/pypy3.11/multiprocessing/pool.py:183 (Pool.__init__)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_03 (broad stdlib), fusil, fleet_10 (broad stdlib) -- reproduced from a bare call |
| **Defect class** | `crash-instead-of-clean-failure-at-allocation-limit` |
| **Reduced from** | 22249-line generated script -> 4 lines |
| **CPython** | PyPy-only. raises `RuntimeError: can't start new thread` cleanly -- 6/6 at EVERY limit from 1024 MiB down to 128 MiB (CPython 3.14.3), and 0/10 under an identical limit and ballast. Never segfaults. |

## Reproducer

```python
`multiprocessing.dummy.Pool()` under `ulimit -v 524288` (512 MiB) -- no ballast needed
```

PyPy surfaces this as:

```
Fatal Python error: Segmentation fault, in _repopulate_pool_static
```

## Analysis

The benign outcome, which PyPy produces most of the time and is presumably the intended one, is `AttributeError: 'DummyProcess' object has no attribute 'terminate'` from Pool.__init__'s own cleanup path. The bug is that the same situation sometimes segfaults instead. The crash needs the process in a narrow band below the limit -- enough address space to start the pool, not enough to finish -- and the band moves between machines AND between edits of the reproducer file itself: adding a docstring moved it by 150 MiB. A self-calibrating variant (fill, then release fixed headroom) does NOT reproduce it, so the ballast is not merely a proxy for 'nearly full'. Hence the sweep.

fleet_10 (2026-09-05) sharpened this. The ballast is NOT required: a bare `multiprocessing.dummy.Pool()` under `ulimit -v 524288` segfaults 6/8 on its own, because the interpreter's own startup already puts it in the band. An RLIMIT_AS sweep of that bare call, 6 runs each: unlimited / 3072 / 2048 / 1536 MiB all clean; 1024 and 768 MiB give `can't start new thread` 6/6; 512 MiB gives 4 SEGV + 2 clean. Three further facts:
  * The fault is UNCATCHABLE. Wrapping the call in `try/except BaseException`, 6 of 8 runs never reach the handler and never print, so this is a hard SIGSEGV inside construction -- not an exception, and not a `__del__`/teardown problem.
  * It is NOT PyPy thread bootstrap in general. Starting 4096 live threads until exhaustion raises `can't start new thread` cleanly on BOTH PyPy and CPython, so the defect is specific to the pool-construction path (`_repopulate_pool_static`'s `w.start()` loop).
  * The band's position relative to a fuzzing run's own limit is NOT stable: here it sits well BELOW the fleet's 3072 MiB (which is why 60 straight replays in fleet_08 found nothing), while in fleet_09's `--concurrency-stress` configuration it sat ABOVE it. Sweep; never assume a direction.

## Prior art

Unreported. NOT seeded in the toolkit catalog (added to the report after hand-over). The single highest-volume signature of the whole campaign: 13 of 58 kept dirs in one fleet and 5 in another, across every instance.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
