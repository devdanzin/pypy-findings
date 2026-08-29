# pypy-findings

A catalog of **bugs in [PyPy](https://github.com/pypy/pypy)** found by fuzzing it with
[**fusil**](https://github.com/devdanzin/fusil), each reduced to a minimal reproducer and
confirmed against CPython as a differential oracle.

Sibling of [`pypy-review-findings`](https://github.com/devdanzin/pypy-review-findings), which
catalogs bugs found by *static review* of PyPy's RPython source with
`pypy-review-toolkit`. The two are largely disjoint and were built independently; where they
overlap, both records say so.

## The findings

**16 findings, all reproduced.** [**INDEX.md**](INDEX.md) is the table;
[`catalog/known_bugs.tsv`](catalog/known_bugs.tsv) is the machine-readable form.

Reproduced on **PyPy 7.3.23** (`194f9f44b505`, Python 3.11.15), with **CPython 3.14.3** as the
oracle. Every reproducer ships with the captured output from both interpreters in
`evidence.txt`.

Highlights:

- **`PYPY-FUZZ-001` / `008` / `012`** — three different consumers of one apparent producer.
  An invalid UTF-8 byte becomes an out-of-range "codepoint", and whichever code meets it next
  fails its own way: an RPython assertion (`Fatal RPython error`, an uncatchable abort), a
  `KeyError` from the unicodedata table, or a `CheckError` from the string formatter. Two
  bytes of input each. Worth fixing at the producer.
- **`PYPY-FUZZ-013`** — `_io.BufferedRWPair.__new__(_io.BufferedRWPair).closed` segfaults.
  One line. Every other type in the family raises
  `ValueError: I/O operation on uninitialized object`.
- **`PYPY-FUZZ-011`** — `memoryview._pypy_raw_address()` on a released view segfaults. 14 of
  the type's other members raise cleanly; this is the one that hands back a raw pointer.
- **`PYPY-FUZZ-006` / `007` / `009`** — three *different* things happen at an address-space
  limit: PyPy's intended clean `out of memory` abort, a SIGSEGV, and glibc reporting heap
  corruption. Only the first is correct.
- **`PYPY-FUZZ-015`** — two threads sharing `for line in f` segfault at EOF. Ordinary code,
  no fuzzer scaffolding. It needs the text layer and it needs to reach EOF; every
  `BufferedReader`, `BytesIO` and `StringIO` variant is clean at five stream lengths.
- **`PYPY-FUZZ-016`** — `list(z)` twice on one `itertools.zip_longest` segfaults. Three lines,
  no threads, 12/12. A retired sub-iterator is stored as `None` and read back unguarded by a
  method copied from `map`/`zip`, where that can never happen — so `list`, `set`, `sorted`,
  `min` and `[*z]` fault while a plain `for` loop over the same object is fine.

## The recurring shape

Four findings — `005`, `011`, `013`, `014` — are the same defect: **a member that skips an
invalidation or initialization guard its siblings all apply**, then dereferences. In each case
the guard demonstrably exists elsewhere on the same type or in the same family, so these are
omissions rather than design choices:

| finding | the member | what its siblings do |
|---|---|---|
| `005` | `TextIOWrapper._dealloc_warn` | 17 sibling methods call `_check_attached` |
| `011` | `memoryview._pypy_raw_address` | 14 of 19 members raise `ValueError` |
| `013` | `_io.BufferedRWPair.closed` | 4 sibling types raise `ValueError` |
| `014` | `_hashlib.HMAC.block_size` | checks the result of the call, not the argument |

That is a better ask of maintainers than four one-line patches: a systematic audit of which
members check the sentinel state and which do not would likely find more.

`PYPY-FUZZ-016` is the mirror image and worth stating separately: there the method was
*copied* from two siblings where it is correct (`map` and `zip` never retire a sub-iterator),
into a class that does retire them. Nobody omitted a guard; an invariant was carried across a
copy that does not hold on the far side. Both shapes point at the same audit, from opposite
directions.

## Fixes that did not propagate

Three findings are the same defect class as issues the author previously filed on the PyPy
tracker **and got fixed** — at doors the fix did not reach. Each prior reproducer was
re-tested on 7.3.23 on 2026-08-27:

| prior issue | its own reproducer, today | still-live finding here |
|---|---|---|
| [#5111](https://github.com/pypy/pypy/issues/5111) `_string.formatter_field_name_split` CheckError | fixed | `PYPY-FUZZ-012` |
| [#5140](https://github.com/pypy/pypy/issues/5140) / [#5126](https://github.com/pypy/pypy/issues/5126) StringIO invalid state | fixed | `PYPY-FUZZ-013` |
| [#5127](https://github.com/pypy/pypy/issues/5127) `_keccak_init` glibc abort | fixed | `PYPY-FUZZ-014` |
| [#5123](https://github.com/pypy/pypy/issues/5123) `_dealloc_warn` detached | **still segfaults** | `PYPY-FUZZ-005` |

Searching the tracker by keyword is not enough here: those issues name different *types* in
their titles, so a keyword search misses them. Re-running a closed issue's own reproducer on
the current build is the check that works.

## Reproducing

```bash
python scripts/capture_evidence.py --only PYPY-FUZZ-013 \
    --pypy /path/to/pypy3.11 --cpython /path/to/python3
```

Four findings (`006`, `007`, `009`, `010`) need the process near an **address-space limit** —
they are invisible without one, which is why fusil found them and an ordinary test run would
not. Their reproducers apply `RLIMIT_AS` themselves and **sweep** a range rather than
hardcoding a value: the window is narrow and moves between machines, PyPy builds, and even
edits to the reproducer file. On one of them, adding a docstring moved the window by 150 MiB.

`PYPY-FUZZ-010` is a race and is honest about it: 12/12 on the original 11 735-line script,
3/12 on the 109-line reduction. A rate below 1/1 is not a failed reproduction, and the
`reliability` field records the measured rate for every finding rather than a bare
"reproduced".

## A correction, kept in the open

`PYPY-FUZZ-015` claimed until 2026-08-28 that the crash required "the text layer over a **real
file descriptor**", and built a mechanism on it. The descriptor half was wrong. The row it
rested on — `TextIOWrapper(BytesIO)` measuring 0/6 — used a 1000-line stream while every case
it was compared against was short, at a fixed iteration count, so it was the only row that
never reached EOF: its 0/6 measured the missing exhaustion, not the missing descriptor. Held
constant, it faults 6/6.

The reproducer now sweeps stream length as well as stream kind, which is what the original
comparison should have done, and the record says what changed and why. The text-layer half
survived the re-test and is stronger for it — four non-text stream kinds are 0/6 at every
length.

## How records are maintained

`scripts/records.py` is the single source of truth. `meta.json`, `report.md`, `INDEX.md` and
`catalog/known_bugs.tsv` are all generated from it by `scripts/regen_derived.py` and must
never be hand-edited — a correction goes into `records.py` and is regenerated. CI runs
`validate_records.py` (schema plus evidence-grade checks) and `regen_derived.py --check`
(a guard that nothing generated has drifted).

See [`MINTING.md`](MINTING.md) for what earns an id.

## Status

**None of these 16 are filed upstream.** The first fifteen are mirrored as rows in
`pypy-review-toolkit`'s `pypy_known_bugs.tsv`, so its `known-issues` command can
cross-reference them against scanner output; `PYPY-FUZZ-016` is not seeded there yet. `005` is additionally pinned to a source line by
`pypy-review-findings` as `PYPYR-0001`, with `PYPYR-0002` recording a second route to the same
site that this catalog's reproducer does not exercise.
