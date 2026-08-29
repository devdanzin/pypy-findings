# PYPY-FUZZ-015 — Two threads calling `next()` on one shared TEXT-stream iterator segfault at EOF

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SIGSEGV |
| **Status** | `reproduced` |
| **Reliability** | a race, so a rate rather than a verdict, and the rate depends almost entirely on how fast the stream reaches EOF. Driven to exhaustion it is 6/6 on both a real file and a BytesIO-backed text layer; left unexhausted it is 0/6 on either. The shipped table reports every cell. Wrapped in 20 rounds the minimal form is 6/6 (CPython 0/6); the 335-line reduction is 11/12 single runs. Two threads suffice; one thread is 0/6 |
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

Ordinary code -- `for line in f` shared between threads -- with no ctypes, no address-space limit and no fuzzer scaffolding. TWO conditions are required. (1) The stream must be the TEXT layer: io.TextIOWrapper over anything faults, while io.BufferedReader(io.FileIO(...)), io.BufferedReader(io.BytesIO(...)), a bare io.BytesIO and a bare io.StringIO are 0/6 at every stream length tried (1, 3, 50, 500 and 5000 lines). (2) The threads must actually EXHAUST the iterator: holding the stream kind fixed, 400 advances over a 5000-line stream is 0/6 and 40000 advances over the same stream is 6/6. A REAL FILE DESCRIPTOR IS NOT REQUIRED -- this catalog said it was until 2026-08-28, and that was wrong. The original table compared a 1000-line io.TextIOWrapper(io.BytesIO(...)) against short fd-backed streams at a fixed 200 iterations, so the BytesIO row was the only one that never reached EOF and its 0/6 measured the missing exhaustion, not the missing descriptor. Re-run with exhaustion held constant, io.TextIOWrapper(io.BytesIO(...)) faults 6/6. The descriptor does still affect the RATE -- fd-backed streams fault at lengths where BytesIO-backed ones do not -- but not whether it can happen. So the defect is in the text layer's own decoder/readahead state, which two threads can be inside at once with nothing serialising them; the GIL, which makes most PyPy threading safe by accident, does not cover it here. Found by --concurrency-stress, a mode whose own generated scripts print "GIL enabled; running serialised" and which was expected to find deadlocks and re-entrancy rather than anything race-shaped.

## Prior art

Unreported.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
