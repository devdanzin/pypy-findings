# PYPY-FUZZ-009 — glibc reports heap corruption at an address-space limit, where PyPy's own exhaustion abort is clean

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | process abort |
| **Status** | `reproduced` |
| **Reliability** | 8/8 at 3072 MiB; two distinct windows (1536 and 3072), narrow |
| **Needs an address-space limit** | yes — needs the child address-space limit (`--child-memory-limit-mb`) |
| **Site(s)** | _not pinned — see below_ |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_05 and fleet_06 (broad stdlib) |
| **Defect class** | `crash-instead-of-clean-failure-at-allocation-limit` |
| **Reduced from** | 21624-line generated script -> 247 lines |
| **CPython** | PyPy-only. clean at every cap tested (1024/2048/3072/4096 MiB) |

## Reproducer

```python
see repro.py -- sweeps RLIMIT_AS over a 247-line reduced fuzz script
```

PyPy surfaces this as:

```
free(): double free detected in tcache 2
```

## Analysis

Reproduced in TWO unrelated modules -- functools and importlib.resources._common, in different fleet instances -- which is what argues this is interpreter-level rather than something about one module. MECHANISM UNKNOWN, and two hypotheses were tested and killed: (a) a mishandled thread-bootstrap allocation, since the session logs `Failed to create thread ...: MemoryError` just before the abort -- but starting 4000 threads under the limit with 0-3000 MiB of ballast produced no corruption on either interpreter; (b) libmpdec through cffi, since the reduction builds huge Decimals -- but PyPy has no `_decimal` module at all, so that code takes the pure-Python fallback and no foreign allocator is involved. A four-point cap sweep finds the 3072 window and MISSES the 1536 one entirely, which is the argument for sweeping finely.

## Prior art

Unreported. Distinct from PYPY-FUZZ-006/007 by face: measured across five caps on the 006 case, PyPy's aborts are ALWAYS its clean "out of memory: couldn't allocate the next arena", never a glibc message. Three outcomes exist at a limit and this is the third.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
