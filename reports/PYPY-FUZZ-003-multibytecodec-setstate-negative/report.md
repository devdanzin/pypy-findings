# PYPY-FUZZ-003 — Multibyte incremental encoder `setstate()` passes a negative value to `rbigint.tobytes`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SystemError leak |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | `MultibyteIncrementalEncoder_setstate_w -> rbigint.tobytes` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_02 (broad stdlib) |
| **Defect class** | `unvalidated-rpython-helper-call` |
| **Reduced from** | fleet dirs (62 of them) -> 1 line |
| **CPython** | PyPy-only. raises OverflowError: can't convert negative int to unsigned |

## Reproducer

```python
import codecs; codecs.getincrementalencoder('cp949')().setstate(-1)
```

PyPy surfaces this as:

```
SystemError: unexpected internal exception (please report a bug): <InvalidSignednessError object ...>
```

## Analysis

All 12 multibyte encoders plus StreamWriter are affected; the decoders are not. `int.to_bytes` is guarded, which makes `setstate` the one unvalidated `rbigint.tobytes` caller on this path.

## Prior art

Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-003. The static catalog's PYPYR-0007 finds a third unstated precondition of the same helper (`nbytes >= 0` via `(0).to_bytes(-1)`), so `rbigint.tobytes` has now been reached unguarded from two independent directions.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
