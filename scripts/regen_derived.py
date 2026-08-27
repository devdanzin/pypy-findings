#!/usr/bin/env python3
"""Generate every derived artifact from `records.py`.

`records.py` is the source of truth. `meta.json`, `report.md`, `INDEX.md` and
`catalog/known_bugs.tsv` are all generated here and must never be hand-edited -- a correction
goes into `records.py` and is regenerated, so the catalog cannot drift from itself.

Usage:
    python scripts/regen_derived.py [--check]

`--check` regenerates into memory and exits non-zero if anything on disk differs, which is
what CI runs.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import CONFIRMED_BUILD, CPYTHON_ORACLE, FUZZER, RECORDS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

KIND_LABEL = {
    "segv": "SIGSEGV",
    "abort": "process abort",
    "sigill": "SIGILL",
    "systemerror-leak": "SystemError leak",
    "divergence": "behavioural divergence",
}


def report_dir(rec):
    return ROOT / "reports" / f"{rec['id']}-{rec['slug']}"


def meta_for(rec):
    return {
        "id": rec["id"],
        "slug": rec["slug"],
        "title": rec["title"],
        "short_title": rec["short"],
        "kind": rec["kind"],
        "signatures": rec["sites"],
        "one_line_repro": rec["repro"].replace("\n", "; "),
        "repro": rec.get("repro_file"),
        "evidence": "evidence.txt" if rec.get("repro_file") else None,
        "status": rec["status"],
        "reliability": rec["reliability"],
        "needs_rlimit": rec["needs_rlimit"],
        "reduced_from": rec["reduced_from"],
        "confirmed_build": CONFIRMED_BUILD,
        "cpython_oracle": CPYTHON_ORACLE,
        "found_by": rec["found_by"],
        "defect_class": rec["defect_class"],
        "shared_with_cpython": rec["shared_with_cpython"],
        "cpython_behavior": rec["cpython_behavior"],
        "prior_art": rec["prior_art"],
        "leak_signature": rec.get("leak_signature"),
        "notes": rec["analysis"],
    }


def report_for(rec):
    sites = ", ".join("`" + s + "`" for s in rec["sites"]) if rec["sites"] else "_not pinned — see below_"
    rlimit = (
        "yes — needs the child address-space limit (`--child-memory-limit-mb`)"
        if rec["needs_rlimit"] else "no"
    )
    lines = [
        f"# {rec['id']} — {rec['title']}",
        "",
        "> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.",
        "",
        "| | |",
        "|---|---|",
        f"| **Kind** | {KIND_LABEL.get(rec['kind'], rec['kind'])} |",
        f"| **Status** | `{rec['status']}` |",
        f"| **Reliability** | {rec['reliability']} |",
        f"| **Needs an address-space limit** | {rlimit} |",
        f"| **Site(s)** | {sites} |",
        f"| **Confirmed on** | {CONFIRMED_BUILD} |",
        f"| **Oracle** | {CPYTHON_ORACLE} |",
        f"| **Found by** | {', '.join(rec['found_by'])} |",
        f"| **Defect class** | `{rec['defect_class']}` |",
        f"| **Reduced from** | {rec['reduced_from']} |",
        f"| **CPython** | {'**Shared with CPython.** ' if rec['shared_with_cpython'] else 'PyPy-only. '}"
        f"{rec['cpython_behavior']} |",
        "",
        "## Reproducer",
        "",
        "```python",
        rec["repro"],
        "```",
        "",
    ]
    if rec.get("leak_signature"):
        lines += ["PyPy surfaces this as:", "", "```", rec["leak_signature"], "```", ""]
    lines += ["## Analysis", "", rec["analysis"], "", "## Prior art", "", rec["prior_art"], ""]
    if rec.get("repro_file"):
        lines += [
            f"Reproducer script: [`{rec['repro_file']}`]({rec['repro_file']}) · "
            f"captured output: [`evidence.txt`](evidence.txt)",
            "",
        ]
    return "\n".join(lines)


def index_md():
    by_class = {}
    for rec in RECORDS:
        by_class.setdefault(rec["defect_class"], []).append(rec)
    lines = [
        "# Index",
        "",
        "> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.",
        "",
        f"{len(RECORDS)} findings, all reproduced on {CONFIRMED_BUILD}, "
        f"with {CPYTHON_ORACLE} as the differential oracle.",
        "",
        "| id | kind | short title | reliability | reduced from |",
        "|---|---|---|---|---|",
    ]
    for rec in RECORDS:
        lines.append(
            f"| [`{rec['id']}`](reports/{rec['id']}-{rec['slug']}/report.md) "
            f"| {KIND_LABEL.get(rec['kind'], rec['kind'])} | {rec['short']} "
            f"| {rec['reliability']} | {rec['reduced_from']} |"
        )
    lines += ["", "## By defect class", ""]
    for cls in sorted(by_class):
        ids = ", ".join(f"`{r['id']}`" for r in by_class[cls])
        lines.append(f"- **`{cls}`** ({len(by_class[cls])}) — {ids}")
    lines.append("")
    return "\n".join(lines)


def known_bugs_tsv():
    cols = ["id", "kind", "defect_class", "sites", "reliability", "needs_rlimit",
            "short_title", "found_by", "confirmed_build"]
    rows = ["\t".join(cols)]
    for rec in RECORDS:
        rows.append("\t".join([
            rec["id"], rec["kind"], rec["defect_class"],
            "; ".join(rec["sites"]) or "n/a",
            rec["reliability"], "yes" if rec["needs_rlimit"] else "no",
            rec["short"], "; ".join(rec["found_by"]), CONFIRMED_BUILD,
        ]))
    return "\n".join(rows) + "\n"


def main():
    check = "--check" in sys.argv
    wanted = {}

    for rec in RECORDS:
        d = report_dir(rec)
        wanted[d / "meta.json"] = json.dumps(meta_for(rec), indent=2) + "\n"
        wanted[d / "report.md"] = report_for(rec)
    wanted[ROOT / "INDEX.md"] = index_md()
    wanted[ROOT / "catalog" / "known_bugs.tsv"] = known_bugs_tsv()

    drift = []
    for path, text in wanted.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drift.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    if check:
        if drift:
            print("derived files differ from records.py:", file=sys.stderr)
            for p in drift:
                print("  " + str(p), file=sys.stderr)
            print("\nrun: python scripts/regen_derived.py", file=sys.stderr)
            return 1
        print("all derived files match records.py")
        return 0

    print(f"wrote {len(wanted)} derived files for {len(RECORDS)} records ({FUZZER})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
