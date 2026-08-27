# PYPY-FUZZ-014 — `_hashlib.HMAC.block_size` passes a NULL `ctx` to OpenSSL after a failed `__init__`

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | deterministic (4/4 failing-construction cases) |
| **Needs an address-space limit** | no |
| **Site(s)** | `lib/pypy3.11/_hashlib/__init__.py (HASH.__init__, sets self.ctx = ffi.NULL)`, `lib/pypy3.11/_hashlib/__init__.py:241 (HMAC.block_size)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_07 (--new-uninit variant) |
| **Defect class** | `missing-sibling-guard` |
| **Reduced from** | 13 fleet dirs, all one signature -> 4 lines |
| **CPython** | PyPy-only. CPython forbids constructing _hashlib.HMAC from Python at all (TypeError), so the half-initialized state is unreachable there |

## Reproducer

```python
import _hashlib
h = _hashlib.HMAC.__new__(_hashlib.HMAC)
try:
    h.__init__(0)
except Exception:
    pass
h.block_size
```

PyPy surfaces this as:

```
Segmentation fault (inside OpenSSL's HMAC_CTX_get_md)
```

## Analysis

The mechanism is visible in PyPy's own pure-Python source. `HASH.__init__` sets `self.ctx = ffi.NULL` (twice -- a literally duplicated line), then `py_digest_by_name` raises on an unknown digest name, leaving a LIVE object whose ctx is NULL. `HMAC.block_size` then calls `lib.HMAC_CTX_get_md(self.ctx)` and only afterwards tests `if not md:` -- the check guards the RESULT of the call, which is too late; the fault is inside the call. The object survives its own failed constructor only because `__new__` plus an explicit `__init__` keeps the reference -- a plain `_hashlib.HMAC('nosuchdigest')` also raises but drops the object. The duplicated NULL assignment is worth pointing out on its own: someone was aware NULL is a state this object passes through. Mirror image of PYPY-FUZZ-004 in the same cffi-stdlib family: that assigns a DANGLING pointer after freeing, this assigns NULL and dereferences it.

## Prior art

Unreported. Adjacent to pypy#5127 (`hashlib.shake_128()._keccak_init(())` aborting with `free(): invalid next size (fast)`), filed by this project's author and closed; re-tested 2026-08-27 on 7.3.23: FIXED. The fix did not propagate to HMAC.block_size.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
