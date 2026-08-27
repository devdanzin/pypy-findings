# PYPY-FUZZ-015 — Two threads calling `next()` on one file iterator segfault at EOF

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | 3-6/6 depending on stream and machine load; a race, so the driver reports a rate. Two threads suffice |
| **Needs an address-space limit** | no |
| **Site(s)** | _not pinned — see below_ |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_08 (--concurrency-stress variant) |
| **Defect class** | `unsynchronised-text-layer-at-eof` |
| **Reduced from** | 1739-line generated script -> 335 lines (10/10) -> ~10 lines by hand |
| **CPython** | PyPy-only. does not crash; concurrent iteration is unspecified there but raises or returns interleaved lines |

## Reproducer

```python
import threading
f = open("/dev/null")
it = iter(f)
def w():
    for _ in range(200):
        try: next(it)
        except Exception: pass
ts = [threading.Thread(target=w) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
```

PyPy surfaces this as:

```
Segmentation fault
```

## Analysis

Ordinary code -- `for line in f` shared between threads -- with no ctypes, no address-space limit and no fuzzer scaffolding. TWO conditions are both required, and neither reproduces alone. (1) The threads must actually EXHAUST the iterator: a 5000-line file over 200 iterations is 0/6, the same file over 20000 iterations is 6/6, so the fault is at end-of-file rather than during steady-state reading. (2) The stream must be the TEXT layer over a REAL file descriptor: sys.__stdin__, open(...) and os.fdopen(...) all fault, while io.TextIOWrapper(io.BytesIO(...)) (text layer, no fd) and io.BufferedReader(io.FileIO(...)) (fd, no text layer) are both clean. That split suggests the mechanism: PyPy releases the GIL around the real read() syscall, so two threads can be inside TextIOWrapper.__next__ at once and race its decoder/readahead state, where a BytesIO never releases the GIL and a BufferedReader has no text-decoding state to corrupt. If that is right it is a missing lock around the text layer's buffer, and the GIL -- which makes most PyPy threading safe by accident -- is exactly what stops protecting it here. Found by --concurrency-stress, a mode whose own generated scripts print "GIL enabled; running serialised" and which was expected to find deadlocks and re-entrancy rather than anything race-shaped.

## Prior art

Unreported.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
