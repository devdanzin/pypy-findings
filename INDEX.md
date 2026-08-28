# Index

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

15 findings, all reproduced on PyPy 7.3.23 (194f9f44b505, Python 3.11.15), with CPython 3.14.3 as the differential oracle.

| id | kind | short title | reliability | reduced from |
|---|---|---|---|---|
| [`PYPY-FUZZ-001`](reports/PYPY-FUZZ-001-compile-bytes-number-invalid-utf8-abort/report.md) | process abort | `compile(b"0\x80")` aborts | deterministic | 12742-line generated script (cProfile.runctx) -> 2 bytes |
| [`PYPY-FUZZ-002`](reports/PYPY-FUZZ-002-struct-unpack-u-unvalidated-codepoint/report.md) | SystemError leak | `struct.unpack('u')` leaks OutOfRange | deterministic | 22242-line generated script -> 1 line |
| [`PYPY-FUZZ-003`](reports/PYPY-FUZZ-003-multibytecodec-setstate-negative/report.md) | SystemError leak | `setstate(-1)` leaks InvalidSignednessError | deterministic | fleet dirs (62 of them) -> 1 line |
| [`PYPY-FUZZ-004`](reports/PYPY-FUZZ-004-lzma-decompressor-double-free/report.md) | process abort | `_lzma` double free | deterministic | fleet dirs -> ~10 lines |
| [`PYPY-FUZZ-005`](reports/PYPY-FUZZ-005-textio-dealloc-warn-detached-segv/report.md) | SIGSEGV | `_dealloc_warn` on a detached wrapper | deterministic | fleet dirs -> 3 lines |
| [`PYPY-FUZZ-006`](reports/PYPY-FUZZ-006-gc-cyclic-finalizers-after-caught-memoryerror-segv/report.md) | SIGSEGV | gc.collect() after a caught MemoryError | 4/4 at a 3072 MiB cap in the shipped 5-cap sweep; 6/6 in a separate 6-run measurement. CPython 0/20 across the same five caps | 22125-line generated script -> 14 lines |
| [`PYPY-FUZZ-007`](reports/PYPY-FUZZ-007-threadpool-at-address-space-limit-segv/report.md) | SIGSEGV | `ThreadPool()` at an address-space limit | sweeps; 6-7/10 at the right ballast, 0/10 one step either side | 22249-line generated script -> 4 lines |
| [`PYPY-FUZZ-008`](reports/PYPY-FUZZ-008-compile-bytes-number-out-of-range-keyerror/report.md) | SystemError leak | `compile(b"0\xf5aa")` leaks KeyError | deterministic (27/27 cells on PyPy, 0/27 on CPython) | 12805-line generated script (code.InteractiveConsole.runcode) -> 4 bytes |
| [`PYPY-FUZZ-009`](reports/PYPY-FUZZ-009-glibc-heap-corruption-at-allocation-limit/report.md) | process abort | glibc double free under allocation pressure | 8/8 at 3072 MiB; two distinct windows (1536 and 3072), narrow | 21624-line generated script -> 247 lines |
| [`PYPY-FUZZ-010`](reports/PYPY-FUZZ-010-sigill-after-fork-from-thread/report.md) | SIGILL | SIGILL after fork-from-a-thread | 12/12 on the original script, 3/12 on the 109-line reduction (a race) | 11735-line generated script -> 109 lines |
| [`PYPY-FUZZ-011`](reports/PYPY-FUZZ-011-memoryview-pypy-raw-address-released/report.md) | SIGSEGV | `_pypy_raw_address()` on a released view | deterministic | fleet dirs -> 3 lines |
| [`PYPY-FUZZ-012`](reports/PYPY-FUZZ-012-format-syntaxerror-non-utf8-checkerror/report.md) | SystemError leak | formatting a SyntaxError leaks CheckError | deterministic (6/6 rows on PyPy, 0/6 on CPython) | 12748-line generated script -> 752 -> 53 lines -> 2 bytes |
| [`PYPY-FUZZ-013`](reports/PYPY-FUZZ-013-io-bufferedrwpair-uninitialized-segv/report.md) | SIGSEGV | uninitialized `BufferedRWPair` | deterministic | 27 fleet dirs, all one signature -> 1 line |
| [`PYPY-FUZZ-014`](reports/PYPY-FUZZ-014-hashlib-hmac-block-size-null-ctx/report.md) | SIGSEGV | `HMAC.block_size` on a NULL ctx | deterministic (4/4 failing-construction cases) | 13 fleet dirs, all one signature -> 4 lines |
| [`PYPY-FUZZ-015`](reports/PYPY-FUZZ-015-textio-shared-iterator-concurrent-next/report.md) | SIGSEGV | concurrent next() on a shared file iterator | a race, so a rate rather than a verdict. Minimal 2-thread form: 3-6/6 single runs depending on stream and machine load; wrapped in 20 rounds it is 6/6 (CPython 0/6). The 335-line reduction is 11/12 single runs. Two threads suffice; one thread is 0/4 | 1739-line generated script -> 335 lines (10/10) -> ~10 lines by hand |

## By defect class

- **`crash-after-fork-from-thread`** (1) — `PYPY-FUZZ-010`
- **`crash-instead-of-clean-failure-at-allocation-limit`** (3) — `PYPY-FUZZ-006`, `PYPY-FUZZ-007`, `PYPY-FUZZ-009`
- **`dangling-pointer-after-free`** (1) — `PYPY-FUZZ-004`
- **`missing-sibling-guard`** (4) — `PYPY-FUZZ-005`, `PYPY-FUZZ-011`, `PYPY-FUZZ-013`, `PYPY-FUZZ-014`
- **`out-of-range-codepoint-from-invalid-utf8`** (3) — `PYPY-FUZZ-001`, `PYPY-FUZZ-008`, `PYPY-FUZZ-012`
- **`unsynchronised-text-layer-at-eof`** (1) — `PYPY-FUZZ-015`
- **`unvalidated-rpython-helper-call`** (2) — `PYPY-FUZZ-002`, `PYPY-FUZZ-003`
