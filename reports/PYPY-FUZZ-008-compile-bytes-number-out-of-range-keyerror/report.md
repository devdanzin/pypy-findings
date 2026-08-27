# PYPY-FUZZ-008 — The same tokenizer error path leaks an RPython `KeyError` for bytes that would encode above U+10FFFF

> Generated from `records.py` by `scripts/regen_derived.py`. Do not hand-edit.

| | |
|---|---|
| **Kind** | SystemError leak |
| **Status** | `reproduced` |
| **Reliability** | deterministic (27/27 cells on PyPy, 0/27 on CPython) |
| **Needs an address-space limit** | no |
| **Site(s)** | `pypy_interpreter_pyparser.c:24992 (_maybe_raise_number_error)`, `rpython_rlib_unicodedata.c:542 (_db_index)` |
| **Confirmed on** | PyPy 7.3.23 (194f9f44b505, Python 3.11.15) |
| **Oracle** | CPython 3.14.3 |
| **Found by** | fusil, fleet_05 (broad stdlib) |
| **Defect class** | `out-of-range-codepoint-from-invalid-utf8` |
| **Reduced from** | 12805-line generated script (code.InteractiveConsole.runcode) -> 4 bytes |
| **CPython** | PyPy-only. raises a clean SyntaxError |

## Reproducer

```python
compile(b"0\xf5aa", "<s>", "exec")
```

PyPy surfaces this as:

```
SystemError: unexpected internal exception (please report a bug): <KeyError object ...>
```

## Analysis

Where PYPY-FUZZ-001's lead bytes assert, 0xF5-0xFF -- the bytes that could only ever encode a codepoint above U+10FFFF -- instead produce an out-of-range value that is handed to the unicodedata table, which raises KeyError. This face needs TWO further bytes after the lead byte; with fewer, the decoder hits end-of-input first and reports a clean SyntaxError. That is why `b"0\xff"` -- the negative control in the first version of the PYPY-FUZZ-001 reproducer -- looked harmless: it was one byte short of a second bug.

## Prior art

Unreported. SECOND FACE of PYPY-FUZZ-001: the same function, a different call site, a different failure. Best reported together with it and with PYPY-FUZZ-012.

Reproducer script: [`repro.py`](repro.py) · captured output: [`evidence.txt`](evidence.txt)
