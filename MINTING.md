# What earns an id

A `PYPY-FUZZ-NNN` id is a claim that someone else can check. The bar is deliberately higher
than "the fuzzer produced a crash directory".

## Required

1. **A reduced reproducer that ships.** Not the generated script — something a reader can
   look at and understand. The `reduced_from` field records both ends of that reduction,
   because a 22 000-line script cut to 14 lines and a 22 000-line script cut to 3 400 are
   different claims about how well the finding is understood.

2. **A measured reliability, stated as a rate.** `8/8` and `3/12` are different claims and a
   bare "reproduced" hides which one a reader is looking at. For anything with a race or a
   threshold, the rate goes in the record and the reproducer reports a rate rather than a
   verdict. `validate_records.py` rejects a record without one.

3. **Captured evidence from both interpreters**, in `evidence.txt`, including the exit status.
   For a signal death the status *is* the finding. A record claiming `reproduced` with no
   evidence file on disk fails validation — that is the one failure mode a catalog like this
   cannot tolerate.

4. **A differential, or an explicit statement of why there isn't one.** Usually CPython on the
   same input. Where no differential is possible — `PYPY-FUZZ-011` tests a PyPy-only method,
   `PYPY-FUZZ-014` needs a construction CPython forbids outright — the record says so and
   argues from *internal* inconsistency instead: what the type's own siblings do.

5. **Prior art actually checked.** Keyword-searching the tracker is not sufficient and has
   already produced a wrong "unreported" claim in this catalog's history: closed issues
   describing the same defect named different types in their titles. Where a related issue
   exists, the record says whether that issue's own reproducer still fails on the current
   build.

## Not enough on its own

- A crash that only the harness can trigger. Anything reachable solely through fusil's own
  bomb objects or generated scaffolding is fuzzer self-noise, not a target bug, and belongs in
  a fusil fix instead — several were, over the course of this campaign.
- A crash CPython shares. Those are a shared contract, not a PyPy bug. Record them in
  `catalog/` prose if useful, without an id.
- An int reinterpreted as a pointer. `_rawffi`, `_cffi_backend`, `ctypes` and friends segfault
  by contract on a fuzzer-chosen integer, and CPython's `ctypes` does the same. Measured, not
  assumed.
- A guess at a mechanism. `analysis` states what was measured; where the mechanism is unknown
  it says so, and says which hypotheses were tested and killed — `PYPY-FUZZ-009` carries two.

## Splitting and merging

Two faces of one function get two ids when they fail differently and need different
reproducers (`PYPY-FUZZ-001` aborts, `PYPY-FUZZ-008` leaks a `KeyError`), with each record
naming the other. They stay adjacent in the numbering and the report argues for fixing the
shared producer rather than each consumer.

Conversely, one id covers several *entry points* into the same defect when a single reproducer
demonstrates them all — `PYPY-FUZZ-013` faults through seven operations, but all seven consult
`.closed`, so it is one record with the surface sweep in the analysis.
