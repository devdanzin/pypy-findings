#!/usr/bin/env python3
"""Run every reproducer on both interpreters and write `evidence.txt` next to it.

The evidence file is what lets a reader check a claim without owning the build, so it records
the exact interpreters, the exact command, and BOTH sides of the differential -- including the
exit status, which for a signal death is the whole finding (`-11` is SIGSEGV, `-6` SIGABRT,
`-4` SIGILL; a shell would report those as 139/134/132).

Reproducers that sweep an address-space range take minutes; that is inherent, see the
`needs_rlimit` field in `records.py`.

Usage:
    python scripts/capture_evidence.py [--only PYPY-FUZZ-0NN] [--pypy PATH] [--cpython PATH]
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import RECORDS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\x1b\[[0-9;]*m")

DEFAULT_PYPY = "/home/danzin/.local/share/uv/python/pypy-3.11.15-linux-x86_64-gnu/bin/pypy3.11"
DEFAULT_CPYTHON = "/home/danzin/venvs/fusil_np_verify/bin/python"

SIGNALS = {-11: "SIGSEGV", -6: "SIGABRT", -4: "SIGILL", -9: "SIGKILL"}
MAX_OUTPUT = 6000


def version(exe):
    p = subprocess.run([exe, "-VV"], capture_output=True, text=True, timeout=60)
    return " ".join((p.stdout + p.stderr).split())


def run(exe, script, cwd, timeout):
    started = time.time()
    try:
        p = subprocess.run(
            [exe, "-u", str(script)], capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL, cwd=str(cwd),
        )
    except subprocess.TimeoutExpired:
        return "timed out after %ds" % timeout, "(timeout)", timeout
    status = SIGNALS.get(p.returncode, "exit %d" % p.returncode)
    out = ANSI.sub("", p.stdout + p.stderr)
    if len(out) > MAX_OUTPUT:
        out = out[:MAX_OUTPUT] + "\n... (truncated)\n"
    return status, out, time.time() - started


def capture(rec, pypy, cpython, timeout):
    d = ROOT / "reports" / f"{rec['id']}-{rec['slug']}"
    script = d / rec["repro_file"]
    if not script.is_file():
        print("  no repro file, skipping")
        return None

    py_status, py_out, py_secs = run(pypy, script, d, timeout)
    cp_status, cp_out, cp_secs = run(cpython, script, d, timeout)

    return "\n".join([
        f"{rec['id']} — {rec['short']}",
        "=" * 78,
        "",
        f"Captured by scripts/capture_evidence.py. Reliability: {rec['reliability']}.",
        f"Needs an address-space limit: {'yes' if rec['needs_rlimit'] else 'no'}"
        + (" (the reproducer applies it itself)" if rec["needs_rlimit"] else "") + ".",
        "",
        f"PyPy    : {version(pypy)}",
        f"CPython : {version(cpython)}",
        f"Command : <interpreter> -u {rec['repro_file']}",
        "",
        "The exit status below is the REPRODUCER DRIVER's, not the finding's. Most drivers exit",
        "1 when the bug reproduces; the differential-table drivers (PYPY-FUZZ-001/008) exit 0",
        "when every measured outcome matched what the record documents -- crashes included. Read",
        "the body, not the status.",
        "",
        "-" * 78,
        f"PyPy — {py_status} ({py_secs:.1f}s)",
        "-" * 78,
        py_out.rstrip(),
        "",
        "-" * 78,
        f"CPython — {cp_status} ({cp_secs:.1f}s)",
        "-" * 78,
        cp_out.rstrip(),
        "",
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--pypy", default=os.environ.get("PYPY", DEFAULT_PYPY))
    ap.add_argument("--cpython", default=os.environ.get("CPYTHON", DEFAULT_CPYTHON))
    ap.add_argument("--timeout", type=int, default=1200)
    args = ap.parse_args()

    for exe in (args.pypy, args.cpython):
        if not Path(exe).is_file():
            sys.exit(f"interpreter not found: {exe}")

    written = 0
    for rec in RECORDS:
        if args.only and rec["id"] != args.only:
            continue
        print(f"{rec['id']} ...", flush=True)
        text = capture(rec, args.pypy, args.cpython, args.timeout)
        if text is None:
            continue
        d = ROOT / "reports" / f"{rec['id']}-{rec['slug']}"
        (d / "evidence.txt").write_text(text, encoding="utf-8")
        written += 1
        print(f"  wrote evidence.txt ({len(text)} bytes)", flush=True)

    print(f"\n{written} evidence file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
