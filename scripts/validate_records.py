#!/usr/bin/env python3
"""Schema and evidence-grade checks over `records.py`.

The rules encode what this catalog promises a reader, so that a row cannot claim more than
the artifacts behind it support:

  * every record has the required fields, a unique id, and a slug matching its directory;
  * `status: reproduced` requires a reproducer script AND a captured `evidence.txt` that
    actually exists on disk -- a claim of reproduction with no shipped evidence is the one
    failure mode a catalog like this cannot tolerate;
  * `reliability` must be stated for every record, because "8/8" and "3/12" are different
    claims and a bare "reproduced" hides which one a reader is looking at;
  * a record that needs an address-space limit must say so, since its reproducer silently
    does nothing without one.

Usage: python scripts/validate_records.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import RECORDS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "id", "slug", "title", "short", "kind", "sites", "repro", "status", "reliability",
    "needs_rlimit", "reduced_from", "found_by", "defect_class", "shared_with_cpython",
    "cpython_behavior", "prior_art", "analysis",
]
KINDS = {"segv", "abort", "sigill", "systemerror-leak", "divergence"}
STATUSES = {"reproduced", "static-confirmed"}


def main():
    errors = []
    seen_ids = set()

    for i, rec in enumerate(RECORDS):
        where = rec.get("id", f"record #{i}")

        for field in REQUIRED:
            if field not in rec:
                errors.append(f"{where}: missing required field {field!r}")
        if errors and where.startswith("record #"):
            continue

        if rec["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(rec["id"])

        if rec.get("kind") not in KINDS:
            errors.append(f"{where}: kind {rec.get('kind')!r} not in {sorted(KINDS)}")
        if rec.get("status") not in STATUSES:
            errors.append(f"{where}: status {rec.get('status')!r} not in {sorted(STATUSES)}")
        if not str(rec.get("reliability", "")).strip():
            errors.append(f"{where}: reliability must be stated")
        if not isinstance(rec.get("needs_rlimit"), bool):
            errors.append(f"{where}: needs_rlimit must be a bool")
        if not isinstance(rec.get("sites"), list):
            errors.append(f"{where}: sites must be a list (empty is fine when not pinned)")
        if not isinstance(rec.get("found_by"), list) or not rec["found_by"]:
            errors.append(f"{where}: found_by must be a non-empty list")

        d = ROOT / "reports" / f"{rec['id']}-{rec['slug']}"
        if not d.is_dir():
            errors.append(f"{where}: missing report directory {d.name}")
            continue

        if rec["status"] == "reproduced":
            repro_file = rec.get("repro_file")
            if not repro_file:
                errors.append(f"{where}: status 'reproduced' requires a repro_file")
            elif not (d / repro_file).is_file():
                errors.append(f"{where}: repro_file {repro_file!r} not on disk")
            if not (d / "evidence.txt").is_file():
                errors.append(f"{where}: status 'reproduced' requires evidence.txt on disk")
            elif not (d / "evidence.txt").read_text(encoding="utf-8", errors="replace").strip():
                errors.append(f"{where}: evidence.txt is empty")

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        return 1

    print(f"{len(RECORDS)} records valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
