# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

A catalog of PyPy bugs found by fuzzing with [fusil](https://github.com/devdanzin/fusil).
One directory per finding under `reports/`, each with a reproducer, captured evidence from
both interpreters, and an analysis.

Sibling repo: [`pypy-review-findings`](https://github.com/devdanzin/pypy-review-findings) —
same subject, found by *static review* instead. Its conventions were the model for this one.
When a finding appears in both, each record must name the other.

## The one rule that matters

**`scripts/records.py` is the only file you edit by hand.** `meta.json`, `report.md`,
`INDEX.md` and `catalog/known_bugs.tsv` are generated from it:

```bash
python scripts/regen_derived.py          # regenerate
python scripts/regen_derived.py --check  # CI: fail if anything drifted
python scripts/validate_records.py       # CI: schema + evidence-grade checks
```

A correction goes into `records.py` and is regenerated. Never hand-edit a generated file —
CI will catch it, and the catalog would otherwise drift from itself.

## Environment

```
PyPy    /home/danzin/.local/share/uv/python/pypy-3.11.15-linux-x86_64-gnu/bin/pypy3.11
CPython /home/danzin/venvs/fusil_np_verify/bin/python
```

Both are defaults in `scripts/capture_evidence.py`; override with `--pypy` / `--cpython` or
the `PYPY` / `CPYTHON` environment variables.

```bash
python scripts/capture_evidence.py                      # all findings
python scripts/capture_evidence.py --only PYPY-FUZZ-013 # one
```

Four findings (`006`, `007`, `009`, `010`) sweep an address-space range and take minutes.
That is inherent, not a bug in the tooling.

## Adding a finding

Read [`MINTING.md`](MINTING.md) first — the bar is higher than "the fuzzer crashed". Then:

1. Add a dict to `RECORDS` in `scripts/records.py`.
2. `mkdir reports/PYPY-FUZZ-0NN-slug/` and put the reproducer in it.
3. `python scripts/capture_evidence.py --only PYPY-FUZZ-0NN`
4. `python scripts/regen_derived.py`
5. `python scripts/validate_records.py`

## Things this catalog has already got wrong once

- **Keyword-searching the tracker is not a prior-art check.** It produced a wrong
  "unreported" claim here: the relevant closed issues named different *types* in their
  titles. Re-run a closed issue's own reproducer on the current build instead. Three findings
  turned out to be fixes that did not propagate — a much stronger thing to report than a
  "new" bug.
- **A single-run interestingness test is wrong for a probabilistic crash.** It reads "no crash
  this run" as "not interesting" and deletes load-bearing code. During `PYPY-FUZZ-010`'s
  reduction that produced a confident 270-line "answer" that reproduces 0/6 — a dead file.
  Use a predicate that accepts on the first hit in N runs, and re-measure the rate at the end.
- **Never hardcode an address-space cap.** The window is narrow and moves between machines,
  builds, and edits to the reproducer file itself. Sweep.
- **State a rate, not a verdict**, for anything with a race or a threshold.
