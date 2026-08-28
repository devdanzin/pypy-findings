# Issue draft for Bhuvansh — PYPY-FUZZ-015

Paste-ready for <https://github.com/pypy/pypy/issues/new>. Everything below the line is the
issue body; the title is above it.

Two notes before posting:

* **Attribution.** The last line credits fusil and the catalog. Adjust it to however you want
  to split credit — the earlier issues in this series used
  `Found using [fusil](https://github.com/devdanzin/fusil) by @vstinner.`
* **Prior art was checked**, both ways: no tracker issue covers concurrent file iteration
  (`#2531` is 2017-era `requests`/eventlet on PyPy 5.x, unrelated), and this is not a
  surviving door of any closed issue — unlike three other findings in the same catalog, which
  *are*.

---

**Title:** `Concurrent next() on a shared file iterator segfaults at EOF`

---

Two threads iterating the same file object segfault PyPy when they reach end-of-file. No
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

It is a race, so a single run is roughly 5/6 on an idle machine and can be as low as 2/8 on a
busy one. Wrapping it in a loop makes one invocation enough — **6/6** here, and **0/6** on
CPython 3.14.3:

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

### Two conditions are required, and neither reproduces alone

This is the part that seems most useful for tracking down.

**1. The threads must actually exhaust the iterator.** The fault is at EOF, not during
steady-state reading:

| file | iterations per thread | SIGSEGV |
|---|---|---|
| a 5000-line file | 200 | **0/6** — never reaches EOF |
| *the same file* | 20 000 | **6/6** — now exhausted |
| `/dev/null` (empty) | 200 | 4/6 — reaches EOF on the first call |
| a 1-line file | 200 | 6/6 |

**2. The stream must be the text layer over a real file descriptor.** Removing either half
makes it clean:

| stream | text layer | real fd | SIGSEGV |
|---|---|---|---|
| `sys.__stdin__` | yes | yes | **6/6** |
| `open("/dev/null")` | yes | yes | **6/6** |
| `open(<any file>)` | yes | yes | **6/6** |
| `os.fdopen(os.open("/dev/null", os.O_RDONLY))` | yes | yes | **6/6** |
| `io.TextIOWrapper(io.BytesIO(...))` | yes | no | 0/6 |
| `io.BufferedReader(io.FileIO("/dev/null"))` | no | yes | 0/6 |

One thread is also clean (0/4), as expected.

### Suspected mechanism

I have not read the RPython source for this, so treat the following as a hypothesis suggested
by the table rather than a diagnosis.

The `BytesIO` and `BufferedReader` rows are what make it interesting. A `BytesIO`-backed
`TextIOWrapper` has all the same text-decoding state but never performs a syscall; a
`BufferedReader` performs the syscall but has no text-decoding state. Only the combination
faults.

That fits the GIL being released around the real `read()`: two threads can then be inside
`TextIOWrapper.__next__` simultaneously and race its decoder / readahead state, where a
`BytesIO` keeps them serialised and a `BufferedReader` has nothing there to corrupt. If that
is right, this is a missing lock around the text layer's buffer — and the GIL, which makes
most threaded PyPy code safe by accident, is exactly what stops covering it at that point.

Concurrent iteration of one file object is of course unspecified behaviour. CPython's answer
is interleaved or duplicated lines; the report here is only that PyPy's is a segfault.

### Version

```
Python 3.11.15 (194f9f44b505, May 25 2026, 19:34:11)
[PyPy 7.3.23 with GCC 10.2.1 20210130 (Red Hat 10.2.1-11)]
```

Linux x86_64. CPython 3.14.3 used as the differential oracle.

Found with [fusil](https://github.com/devdanzin/fusil) (`--concurrency-stress` mode); full
record, reproducers and captured output from both interpreters as `PYPY-FUZZ-015` in
[pypy-findings](https://github.com/devdanzin/pypy-findings).
