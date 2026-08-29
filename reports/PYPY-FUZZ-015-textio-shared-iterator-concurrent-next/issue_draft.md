# Issue draft for Bhuvansh — PYPY-FUZZ-015

Paste-ready for <https://github.com/pypy/pypy/issues/new>. Everything below the line is the
issue body; the title is above it.

Three notes before posting:

* **This draft was corrected on 2026-08-28.** The first version claimed the crash needed a
  real file descriptor and explained it as the GIL being released around the `read()`
  syscall. That was wrong — the measurement behind it was confounded, and re-running it with
  the confound removed shows `TextIOWrapper(BytesIO)` faults just as hard. If you already
  sent the earlier text anywhere, this replaces it; the mechanism paragraph is the part that
  changed.
* **Attribution.** The last line credits fusil and the catalog. Adjust it to however you want
  to split credit — the earlier issues in this series used
  `Found using [fusil](https://github.com/devdanzin/fusil) by @vstinner.`
* **Prior art was checked**, both ways: no tracker issue covers concurrent text-stream
  iteration (`#2531` is 2017-era `requests`/eventlet on PyPy 5.x, unrelated), and this is not
  a surviving door of any closed issue — unlike three other findings in the same catalog,
  which *are*.

---

**Title:** `Concurrent next() on a shared text-stream iterator segfaults at EOF`

---

Two threads iterating the same text stream segfault PyPy when they reach end-of-file. No
`ctypes`, no resource limits — just `for line in f` shared between threads:

```python
import threading

f = open("/dev/null")
it = iter(f)

def worker():
    for _ in range(200):
        try:
            next(it)
        except Exception:
            pass

threads = [threading.Thread(target=worker) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

```
Fatal Python error: Segmentation fault

Stack (most recent call first, approximate line numbers):
  File "repro.py", line 6 in worker
  File "/.../lib/pypy3.11/threading.py", line 971 in run
  File "/.../lib/pypy3.11/threading.py", line 1028 in _bootstrap_inner
  File "/.../lib/pypy3.11/threading.py", line 988 in _bootstrap
```

It is a race, so a single run is not always a crash. Wrapping it in a loop makes one
invocation enough — **6/6** here, and **0/6** on CPython 3.14.3:

```python
import threading

for _ in range(20):
    f = open("/dev/null")
    it = iter(f)

    def worker():
        for _ in range(200):
            try:
                next(it)
            except Exception:
                pass

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

print("survived")
```

### Two conditions are required

This is the part that seems most useful for tracking down.

**1. The stream must be the text layer.** `io.TextIOWrapper` over anything faults; nothing
else does. Six runs per cell, 2 threads × 200 `next()` calls, sweeping the stream length so
that "reaches EOF quickly" is not confounded with the stream kind:

| stream | 1 line | 3 | 50 | 500 | 5000 |
|---|---|---|---|---|---|
| `io.TextIOWrapper(io.BytesIO(...))` | **6/6** | 0/6 | **5-6/6** | 0/6 | 0/6 |
| `open(<file>)` | **6/6** | **6/6** | **5-6/6** | 0/6 | 0/6 |
| `io.BufferedReader(io.BytesIO(...))` | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| `io.BufferedReader(io.FileIO(...))` | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| `io.BytesIO(...)` | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| `io.StringIO(...)` | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |

**2. The threads must actually exhaust the iterator.** The fault is at end-of-file, not
during steady-state reading. Holding the stream kind fixed and varying only how far the
threads get through a 5000-line stream:

| stream | 400 advances | 40 000 advances |
|---|---|---|
| `open(<5000-line file>)` | 0/6 | **6/6** |
| `io.TextIOWrapper(io.BytesIO(...))` | 0/6 | **6/6** |

That is also why the length row above is not monotonic: a short stream reaches EOF on the
first few calls, a 5000-line one never reaches it within 400 advances, and 50 lines lands in
between.

One thread is clean (0/6); two are enough (6/6); four are no worse.

### What this narrows it to

A real file descriptor is **not** required — `io.TextIOWrapper` over an in-memory `BytesIO`
faults exactly as hard once it is driven to EOF. The descriptor does affect the *rate*
(fd-backed streams fault at lengths where `BytesIO`-backed ones do not, e.g. 6/6 vs 0/6 at
three lines), presumably because a real `read()` is a wider window, but it is not a
precondition and the mechanism does not appear to run through the syscall.

Nor is it the buffered layer: `io.BufferedReader` over *either* a `BytesIO` or a `FileIO` is
clean at every length tried, as is a raw `BytesIO`. And a `StringIO` — which has no decoder
at all — is clean too.

What is left is `TextIOWrapper`'s own decoder / readahead state at end-of-file, which two
threads can be inside simultaneously with nothing serialising them. The GIL makes most
threaded PyPy code safe by accident; whatever happens in that path, it does not cover it.

I have not read the RPython source for `_io`, so treat the last paragraph as the shape the
measurements point at rather than a diagnosis.

Concurrent iteration of one stream is of course unspecified behaviour. CPython's answer is
interleaved or duplicated lines; the report here is only that PyPy's is a segfault.

### Version

```
Python 3.11.15 (194f9f44b505, May 25 2026, 19:34:11)
[PyPy 7.3.23 with GCC 10.2.1 20210130 (Red Hat 10.2.1-11)]
```

Linux x86_64. CPython 3.14.3 used as the differential oracle.

Found with [fusil](https://github.com/devdanzin/fusil) (`--concurrency-stress` mode); full
record, reproducers and captured output from both interpreters as `PYPY-FUZZ-015` in
[pypy-findings](https://github.com/devdanzin/pypy-findings).
