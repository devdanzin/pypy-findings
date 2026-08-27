"""PyPy 3.11 (7.3.23): _hashlib.HMAC.block_size passes a NULL ctx to OpenSSL.

    $ pypy3.11 repro.py

    $ pypy3.11 -c '
    import _hashlib
    h = _hashlib.HMAC.__new__(_hashlib.HMAC)
    try: h.__init__(0)          # raises; leaves self.ctx == ffi.NULL
    except Exception: pass
    h.block_size'
    Segmentation fault (core dumped)

THE MECHANISM IS VISIBLE IN THE PURE-PYTHON SOURCE

`lib/pypy3.11/_hashlib/__init__.py`, `HASH.__init__` (HMAC's base):

    def __init__(self, name=None, copy_from=None, usedforsecurity=True):
        if name is None:
            raise TypeError(...)
        self.ctx = ffi.NULL                     # <-- NULL first
        self.ctx = ffi.NULL                     # <-- (yes, twice)
        self.name = str(name).lower()
        digest_type = py_digest_by_name(self.name, ...)   # <-- RAISES on a bad name
        ...
        self._init_ctx(copy_from, digest_type)  # <-- never reached

and `HMAC.block_size`:

    @property
    def block_size(self):
        md = lib.HMAC_CTX_get_md(self.ctx)      # <-- called BEFORE any NULL check
        if not md:
            raise ValueError("could not get EVP_MD from HMAC_CTX")
        return lib.EVP_MD_block_size(md)

`__init__` sets `ctx` to NULL, then raises on an unsupported digest name -- leaving a live
object whose `ctx` is NULL. `block_size` hands that straight to OpenSSL. The `if not md`
check guards the *result* of the call, which is too late; the fault is inside
`HMAC_CTX_get_md(NULL)`.

The duplicated `self.ctx = ffi.NULL` is worth a mention on its own: someone was clearly aware
that NULL is a state this object passes through.

WHY THE OBJECT SURVIVES ITS OWN FAILED CONSTRUCTOR
--------------------------------------------------
A plain `_hashlib.HMAC("nosuchdigest")` also raises, but the half-built object is dropped, so
nothing can read it. `__new__` + an explicit `__init__` call keeps the reference -- which is
exactly what `--new-uninit` does, and also what happens in any code that separates allocation
from initialization (pickle, copy, deserializers, C-level subclass helpers).

RELATED, SAME MODULE FAMILY
---------------------------
`_lzma.py` in the same stdlib has the mirror-image defect: it assigns a *dangling* pointer
after freeing (`ffi.NONE`, which does not exist, so the name error leaves the old pointer in
place) -- see `../pypy_lzma_double_free/`. Both are PyPy's cffi-based stdlib modules
mishandling the sentinel state of a C pointer they own.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64), 13 of 42 kept dirs in
`fusil-pypy311_fleet_07` (the `--new-uninit` variant fleet).
"""

import re
import subprocess
import sys

_ANSI = re.compile(r"\x1b\[[0-9;]*m")

CASES = [
    ("__init__(0)", "h.__init__(0)", True),
    ("__init__('a')", "h.__init__('a')", True),
    ("__init__(b'a')", "h.__init__(b'a')", True),
    ("__init__('nosuchdigest')", "h.__init__('nosuchdigest')", True),
    ("no __init__ at all", "pass", False),
    ("__init__() (name=None)", "h.__init__()", False),
    ("__init__('sha256') (valid)", "h.__init__('sha256')", False),
]

CHILD = """
import _hashlib
h = _hashlib.HMAC.__new__(_hashlib.HMAC)
try:
    {init}
except BaseException as e:
    print("init raised:", type(e).__name__)
print("reading block_size", flush=True)
print("block_size =", h.block_size)
"""


def probe(init):
    proc = subprocess.run(
        [sys.executable, "-c", CHILD.format(init=init)],
        capture_output=True, stdin=subprocess.DEVNULL,
    )
    if proc.returncode == -11:
        return "SIGSEGV"
    text = _ANSI.sub("", (proc.stdout + proc.stderr).decode("utf-8", "replace"))
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if proc.returncode == 0:
        return lines[-1][:44] if lines else "clean"
    return lines[-1].split(":")[0][:36] if lines else "rc=%d" % proc.returncode


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    try:
        import _hashlib
    except ImportError:
        print("no _hashlib on this interpreter; nothing to test.")
        return 0
    if not hasattr(_hashlib, "HMAC"):
        print("_hashlib has no HMAC attribute here; nothing to test.")
        return 0

    header = "%-30s %-10s %s" % ("construction", "expected", "reading .block_size")
    print(header)
    print("-" * len(header))

    faults = 0
    for label, init, should_fault in CASES:
        got = probe(init)
        if got == "SIGSEGV":
            faults += 1
        print("%-30s %-10s %s" % (label, "SIGSEGV" if should_fault else "safe", got))

    print()
    if faults:
        print("A constructor that raises leaves self.ctx == ffi.NULL, and block_size hands\n"
              "that NULL to OpenSSL's HMAC_CTX_get_md before checking anything.")
        return 1
    if all("TypeError" in probe(init) for _, init, _ in CASES[:1]):
        print("This interpreter forbids constructing _hashlib.HMAC from Python at all\n"
              "(TypeError on every row), so the half-initialized state is unreachable here.\n"
              "That is CPython's behaviour, and it is why there is no CPython differential:\n"
              "the bug needs an object that survives its own failed __init__.")
        return 0
    print("No faults; this build guards the NULL ctx.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
