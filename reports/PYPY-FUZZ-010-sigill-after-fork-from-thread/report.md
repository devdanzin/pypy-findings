# PYPY-FUZZ-010 — SIGILL in the child after `fork()` from a non-main thread, inside `threading._after_fork`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGILL |
| **Status** | `reproduced` |
| **Reliability** | 12/12 on the original script, 3/12 on the 109-line reduction (a race) |
| **Needs an address-space limit** | yes — needs the child address-space limit (`--child-memory-limit-mb`) |
| **Site(s)** | `lib/pypy3.11/_weakrefset.py:122 (discard)`, `lib/pypy3.11/threading.py:1630 (_after_fork)`, `lib/pypy3.11/multiprocessing/popen_fork.py:62 (_launch, its os.fork())` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_05 and fleet_06 (broad stdlib) |
| **Defect class** | `crash-after-fork-from-thread` |
| **Reduced from** | 11735-line generated script -> 109 lines |
| **CPython** | PyPy-only. clean, every run |

## Reproducer

```python
see repro.py -- concurrent multiprocessing.popen_fork.Popen() from worker threads
```

PyPy surfaces this as:

```
Fatal Python error: Illegal instruction
```

## Analysis

`_launch` line 62 is its `os.fork()`. PyPy runs the after-fork hooks in the CHILD, so `threading._after_fork()` executes there and dies walking a weakref set. The whole stack is ordinary Python; an illegal instruction underneath it means either an RPython `ll_assert` compiled to a trap or JIT-emitted code running in a state that no longer holds -- and forking away from a multi-threaded, JIT-warm process is exactly such a state. The trigger includes re-running `__init__` on an ALREADY-CONSTRUCTED Popen: the parent side of `_launch` succeeds even when the argument is not a Process, because the child raises in `process_obj._bootstrap` and `os._exit()`s, which the parent never sees. Three hand-written minimal attempts all failed to reproduce it, including one that does exactly what the reduction does -- see the report.

## Prior art

Unreported. The only SIGILL of the whole campaign, across six fleets.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
