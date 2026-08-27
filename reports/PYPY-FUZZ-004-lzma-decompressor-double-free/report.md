# PYPY-FUZZ-004 — `_lzma` frees a buffer and then stores a name that does not exist, leaving the pointer dangling

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | process abort |
| **Status** | `reproduced` |
| **Reliability** | deterministic |
| **Needs an address-space limit** | no |
| **Site(s)** | `lib_pypy/_lzma.py:~562 (post_decompress_avail_data)`, `lib_pypy/_lzma.py:~575 (clear_input_buffer)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_03 (broad stdlib) |
| **Defect class** | `dangling-pointer-after-free` |
| **Reduced from** | fleet dirs -> ~10 lines |
| **CPython** | PyPy-only. n/a -- CPython's _lzma is C, not this cffi wrapper |

## Reproducer

```python
see repro.py -- LZMADecompressor operations that free and then re-touch the input buffer
```

PyPy surfaces this as:

```
double free or corruption (!prev) / (out)
```

## Analysis

Two defects in one file. The first is a one-character-class typo: after `m.free()` the code assigns `ffi.NONE`, which does not exist (the cffi sentinel is `ffi.NULL`), so the assignment raises and the old, freed pointer stays in place -- a dangling pointer by accident rather than by omission. The second is an unlocked check-then-act in `clear_input_buffer`. PYPY-FUZZ-014 is the mirror image in the same cffi-stdlib family: there the sentinel IS assigned and then dereferenced.

## Prior art

Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-004. Unreported upstream.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
