"""The record seed data. Everything else in this repository is generated from it.

`meta.json`, `report.md`, `INDEX.md` and `catalog/known_bugs.tsv` are all produced by
`scripts/regen_derived.py` and must never be hand-edited -- a correction goes here and is
regenerated, so the catalog cannot drift from itself.

Field notes specific to a FUZZING catalog (see the sibling `pypy-review-findings`, which is a
static-review catalog and carries `reviewed_commit` / `guarded_twin` fields instead):

  reliability   measured hit rate of the shipped reproducer. Recorded for every finding, not
                only the flaky ones, because "8/8" and "3/12" are different claims and a
                reader cannot tell which they are looking at otherwise.
  reduced_from  the size of the generated script the finding came out of. The ratio is the
                honest measure of how much triage a row represents.
  sites         ONLY where a site is actually known -- a shipped `lib_pypy` / `lib/pypy3.11`
                path read directly, or the frames PyPy itself prints in an RPython traceback.
                Left empty rather than guessed: this catalog never read the RPython source at
                a pinned commit, so it cannot pin interpreter-level line numbers the way the
                static catalog does.
  needs_rlimit  whether the reproducer needs the child address-space limit fusil applies
                (`--child-memory-limit-mb`). Four findings are invisible without it.
"""

CONFIRMED_BUILD = "PyPy 7.3.23 (194f9f44b505, Python 3.11.15)"
CPYTHON_ORACLE = "CPython 3.14.3"
FUZZER = "fusil (github.com/devdanzin/fusil)"

RECORDS = [
    dict(
        id="PYPY-FUZZ-001", slug="compile-bytes-number-invalid-utf8-abort",
        title="`compile()` of bytes source aborts the interpreter when a digit is followed by an invalid UTF-8 byte",
        short="`compile(b\"0\\x80\")` aborts",
        kind="abort",
        sites=["pypy_interpreter_pyparser.c:25296 (_maybe_raise_number_error)",
               "pypy_interpreter_pyparser.c:30295 (raise_invalid_unicode_char)"],
        repro='compile(b"0\\x80", "<s>", "exec")',
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="12742-line generated script (cProfile.runctx) -> 2 bytes",
        found_by=["fusil, fleet_02/03 (broad stdlib)"],
        defect_class="out-of-range-codepoint-from-invalid-utf8",
        shared_with_cpython=False,
        cpython_behavior="raises a clean SyntaxError",
        prior_art="Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-001. An RPython AssertionError "
                  "escaping generate_tokens is a recurring class -- pypy#4002 and pypy#5076 (trailing "
                  "backslash, fixed in #5708) are earlier instances; the #5076 trigger no longer crashes on "
                  "7.3.23. This trigger is different: it goes through the NUMBER error path, which those did not.",
        leak_signature="Fatal RPython error: AssertionError",
        analysis="A source given as BYTES whose first token is a NUMBER, immediately followed by a byte that "
                 "cannot begin a valid UTF-8 sequence. Both halves are required: `b\"a\\x80\"` and `b\"\\x80\"` "
                 "both raise cleanly. Measured exhaustively over all 256 values of the byte after a digit, the "
                 "outcome splits exactly along the UTF-8 validity classes: 0x80-0xC1 plus 0xE0 and 0xF0 abort, "
                 "0xF5-0xFF leak a KeyError (PYPY-FUZZ-008), everything else raises SyntaxError. Reaches every "
                 "compilation entry point that accepts bytes -- compile(), exec(), eval() -- so any program that "
                 "compiles untrusted bytes can be aborted by a 2-byte input. It cannot be caught: it is a hard "
                 "abort, not an exception.",
    ),
    dict(
        id="PYPY-FUZZ-002", slug="struct-unpack-u-unvalidated-codepoint",
        title="`struct.unpack('u', ...)` passes an unvalidated 4-byte codepoint to `rutf8.unichr_as_utf8`",
        short="`struct.unpack('u')` leaks OutOfRange",
        kind="systemerror-leak",
        sites=["pypy_module_struct.c:4652 (UnpackFormatIterator_append_utf8)",
               "rpython_rlib.c:10474 (unichr_as_utf8)"],
        repro='import struct; struct.unpack("u", b"abcd")',
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="22242-line generated script -> 1 line",
        found_by=["fusil, fleet_02 (broad stdlib)"],
        defect_class="unvalidated-rpython-helper-call",
        shared_with_cpython=False,
        cpython_behavior="the 'u' format was removed in 3.9; struct.error",
        prior_art="Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-002. The static catalog's PYPYR-0004 "
                  "notes this as the same shape with the range check ABSENT, where PYPYR-0004 has the range "
                  "check present and the surrogate clause absent.",
        leak_signature="SystemError: unexpected internal exception (please report a bug): <OutOfRange object ...>",
        analysis="The 'u' unpack format reads four bytes and hands them to `rutf8.unichr_as_utf8` as a codepoint "
                 "with no range check at all, so any four bytes decoding above U+10FFFF raise RPython's "
                 "`OutOfRange`, which nothing in the struct module catches. One line, no state, no timing.",
    ),
    dict(
        id="PYPY-FUZZ-003", slug="multibytecodec-setstate-negative",
        title="Multibyte incremental encoder `setstate()` passes a negative value to `rbigint.tobytes`",
        short="`setstate(-1)` leaks InvalidSignednessError",
        kind="systemerror-leak",
        sites=["MultibyteIncrementalEncoder_setstate_w -> rbigint.tobytes"],
        repro="import codecs; codecs.getincrementalencoder('cp949')().setstate(-1)",
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="fleet dirs (62 of them) -> 1 line",
        found_by=["fusil, fleet_02 (broad stdlib)"],
        defect_class="unvalidated-rpython-helper-call",
        shared_with_cpython=False,
        cpython_behavior="raises OverflowError: can't convert negative int to unsigned",
        prior_art="Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-003. The static catalog's PYPYR-0007 "
                  "finds a third unstated precondition of the same helper (`nbytes >= 0` via `(0).to_bytes(-1)`), "
                  "so `rbigint.tobytes` has now been reached unguarded from two independent directions.",
        leak_signature="SystemError: unexpected internal exception (please report a bug): "
                       "<InvalidSignednessError object ...>",
        analysis="All 12 multibyte encoders plus StreamWriter are affected; the decoders are not. `int.to_bytes` "
                 "is guarded, which makes `setstate` the one unvalidated `rbigint.tobytes` caller on this path.",
    ),
    dict(
        id="PYPY-FUZZ-004", slug="lzma-decompressor-double-free",
        title="`_lzma` frees a buffer and then stores a name that does not exist, leaving the pointer dangling",
        short="`_lzma` double free",
        kind="abort",
        sites=["lib_pypy/_lzma.py:~562 (post_decompress_avail_data)",
               "lib_pypy/_lzma.py:~575 (clear_input_buffer)"],
        repro="see repro.py -- LZMADecompressor operations that free and then re-touch the input buffer",
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="fleet dirs -> ~10 lines",
        found_by=["fusil, fleet_03 (broad stdlib)"],
        defect_class="dangling-pointer-after-free",
        shared_with_cpython=False,
        cpython_behavior="n/a -- CPython's _lzma is C, not this cffi wrapper",
        prior_art="Seeded in pypy-review-toolkit's catalog as PYPY-FUZZ-004. Unreported upstream.",
        leak_signature="double free or corruption (!prev) / (out)",
        analysis="Two defects in one file. The first is a one-character-class typo: after `m.free()` the code "
                 "assigns `ffi.NONE`, which does not exist (the cffi sentinel is `ffi.NULL`), so the assignment "
                 "raises and the old, freed pointer stays in place -- a dangling pointer by accident rather than "
                 "by omission. The second is an unlocked check-then-act in `clear_input_buffer`. "
                 "PYPY-FUZZ-014 is the mirror image in the same cffi-stdlib family: there the sentinel IS "
                 "assigned and then dereferenced.",
    ),
    dict(
        id="PYPY-FUZZ-005", slug="textio-dealloc-warn-detached-segv",
        title="`TextIOWrapper._dealloc_warn()` on a detached wrapper dereferences a null buffer",
        short="`_dealloc_warn` on a detached wrapper",
        kind="segv",
        sites=["pypy/module/_io/interp_textio.py:847 (per the static catalog's PYPYR-0001)"],
        repro="import sys\nsys.__stdin__.detach()\nsys.__stdin__._dealloc_warn(1)",
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="fleet dirs -> 3 lines",
        found_by=["fusil, fleet_02 (broad stdlib, --test-private)"],
        defect_class="missing-sibling-guard",
        shared_with_cpython=False,
        cpython_behavior="CPython does not expose _dealloc_warn on TextIOWrapper at all",
        prior_art="THIS IS AN INCOMPLETE FIX OF A CLOSED ISSUE. pypy#5123 was filed by this project's author and "
                  "closed; mattip's fix (7bc330cce0f, 2024-11-16) guarded the BUFFERED layer "
                  "(interp_bufferedio.py) and left the TEXT layer alone. Re-tested 2026-08-27 on 7.3.23: the "
                  "original reproducer from #5123 STILL SEGFAULTS. Also seeded as PYPY-FUZZ-005 and pinned to a "
                  "line by the static catalog as PYPYR-0001, with PYPYR-0002 recording a second route "
                  "(`__new__` bypass) that this reproducer does not exercise.",
        leak_signature="Segmentation fault",
        analysis="Buffered Reader/Writer/Random now raise RuntimeError after detach; TextIOWrapper still "
                 "segfaults, while its own read/write/flush/fileno/seek/close all raise "
                 "\"underlying buffer has been detached\". The guard exists on 17 sibling methods of the same "
                 "class. This is the first of four findings in this catalog with that exact shape -- see "
                 "PYPY-FUZZ-011, 013 and 014.",
    ),
    dict(
        id="PYPY-FUZZ-006", slug="gc-cyclic-finalizers-after-caught-memoryerror-segv",
        title="Collecting cyclic finalizable objects after a CAUGHT `MemoryError` segfaults instead of raising",
        short="gc.collect() after a caught MemoryError",
        kind="segv",
        sites=[],
        repro="see repro.py -- fill the heap with cyclic __del__ objects, catch MemoryError, then gc.collect()",
        repro_file="repro.py",
        status="reproduced", reliability="4/4 at a 3072 MiB cap in the shipped 5-cap sweep; 6/6 in a separate 6-run measurement. CPython 0/20 across the same five caps",
        needs_rlimit=True,
        reduced_from="22125-line generated script -> 14 lines",
        found_by=["fusil, fleet_03 (broad stdlib)"],
        defect_class="crash-instead-of-clean-failure-at-allocation-limit",
        shared_with_cpython=False,
        cpython_behavior="exits cleanly, 20/20 across five address-space caps",
        prior_art="Unreported. NOT seeded in the toolkit catalog: it was added to the findings report after the "
                  "five-bug version was handed over.",
        leak_signature="Segmentation fault (and NOT PyPy's clean \"out of memory: couldn't allocate the next "
                       "arena\" abort, whose absence is what distinguishes this from mere exhaustion)",
        analysis="The MemoryError is caught, so at that point the program is in a state Python defines as "
                 "recoverable; collecting the cycles then crashes instead of raising. Every line of the 14 is "
                 "load-bearing, measured 4 runs each: without `__del__` 0/4, without the reference cycle 0/4, "
                 "without the gc.collect() loop 0/4, and -- the interesting one -- without an `import weakref` "
                 "that is NEVER USED, 0/4. Substituting bytearrays, 20000 objects, 20000 dicts or `import "
                 "functools` for that import does not restore it, so the threshold is in the GC heap's SHAPE, "
                 "not its size. The shipped reproducer therefore SWEEPS a range of caps instead of hardcoding "
                 "one.",
    ),
    dict(
        id="PYPY-FUZZ-007", slug="threadpool-at-address-space-limit-segv",
        title="`multiprocessing.pool.ThreadPool()` segfaults when worker-thread creation starts failing",
        short="`ThreadPool()` at an address-space limit",
        kind="segv",
        sites=["lib/pypy3.11/multiprocessing/pool.py:314 (_repopulate_pool_static)",
               "lib/pypy3.11/multiprocessing/pool.py:183 (Pool.__init__)"],
        repro="see repro.py -- allocate ballast under RLIMIT_AS, then ThreadPool()",
        repro_file="repro.py",
        status="reproduced", reliability="sweeps; 6-7/10 at the right ballast, 0/10 one step either side",
        needs_rlimit=True,
        reduced_from="22249-line generated script -> 4 lines",
        found_by=["fusil, fleet_03 (broad stdlib)"],
        defect_class="crash-instead-of-clean-failure-at-allocation-limit",
        shared_with_cpython=False,
        cpython_behavior="raises cleanly under an identical limit and ballast (0/10)",
        prior_art="Unreported. NOT seeded in the toolkit catalog (added to the report after hand-over). "
                  "The single highest-volume signature of the whole campaign: 13 of 58 kept dirs in one fleet "
                  "and 5 in another, across every instance.",
        leak_signature="Fatal Python error: Segmentation fault, in _repopulate_pool_static",
        analysis="The benign outcome, which PyPy produces most of the time and is presumably the intended one, "
                 "is `AttributeError: 'DummyProcess' object has no attribute 'terminate'` from Pool.__init__'s "
                 "own cleanup path. The bug is that the same situation sometimes segfaults instead. The crash "
                 "needs the process in a narrow band below the limit -- enough address space to start the pool, "
                 "not enough to finish -- and the band moves between machines AND between edits of the "
                 "reproducer file itself: adding a docstring moved it by 150 MiB. A self-calibrating variant "
                 "(fill, then release fixed headroom) does NOT reproduce it, so the ballast is not merely a "
                 "proxy for 'nearly full'. Hence the sweep.",
    ),
    dict(
        id="PYPY-FUZZ-008", slug="compile-bytes-number-out-of-range-keyerror",
        title="The same tokenizer error path leaks an RPython `KeyError` for bytes that would encode above U+10FFFF",
        short="`compile(b\"0\\xf5aa\")` leaks KeyError",
        kind="systemerror-leak",
        sites=["pypy_interpreter_pyparser.c:24992 (_maybe_raise_number_error)",
               "rpython_rlib_unicodedata.c:542 (_db_index)"],
        repro='compile(b"0\\xf5aa", "<s>", "exec")',
        repro_file="repro.py",
        status="reproduced", reliability="deterministic (27/27 cells on PyPy, 0/27 on CPython)",
        needs_rlimit=False,
        reduced_from="12805-line generated script (code.InteractiveConsole.runcode) -> 4 bytes",
        found_by=["fusil, fleet_05 (broad stdlib)"],
        defect_class="out-of-range-codepoint-from-invalid-utf8",
        shared_with_cpython=False,
        cpython_behavior="raises a clean SyntaxError",
        prior_art="Unreported. SECOND FACE of PYPY-FUZZ-001: the same function, a different call site, a "
                  "different failure. Best reported together with it and with PYPY-FUZZ-012.",
        leak_signature="SystemError: unexpected internal exception (please report a bug): <KeyError object ...>",
        analysis="Where PYPY-FUZZ-001's lead bytes assert, 0xF5-0xFF -- the bytes that could only ever encode a "
                 "codepoint above U+10FFFF -- instead produce an out-of-range value that is handed to the "
                 "unicodedata table, which raises KeyError. This face needs TWO further bytes after the lead "
                 "byte; with fewer, the decoder hits end-of-input first and reports a clean SyntaxError. That is "
                 "why `b\"0\\xff\"` -- the negative control in the first version of the PYPY-FUZZ-001 reproducer "
                 "-- looked harmless: it was one byte short of a second bug.",
    ),
    dict(
        id="PYPY-FUZZ-009", slug="glibc-heap-corruption-at-allocation-limit",
        title="glibc reports heap corruption at an address-space limit, where PyPy's own exhaustion abort is clean",
        short="glibc double free under allocation pressure",
        kind="abort",
        sites=[],
        repro="see repro.py -- sweeps RLIMIT_AS over a 247-line reduced fuzz script",
        repro_file="repro.py",
        status="reproduced", reliability="8/8 at 3072 MiB; two distinct windows (1536 and 3072), narrow",
        needs_rlimit=True,
        reduced_from="21624-line generated script -> 247 lines",
        found_by=["fusil, fleet_05 and fleet_06 (broad stdlib)"],
        defect_class="crash-instead-of-clean-failure-at-allocation-limit",
        shared_with_cpython=False,
        cpython_behavior="clean at every cap tested (1024/2048/3072/4096 MiB)",
        prior_art="Unreported. Distinct from PYPY-FUZZ-006/007 by face: measured across five caps on the "
                  "006 case, PyPy's aborts are ALWAYS its clean \"out of memory: couldn't allocate the next "
                  "arena\", never a glibc message. Three outcomes exist at a limit and this is the third.",
        leak_signature="free(): double free detected in tcache 2",
        analysis="Reproduced in TWO unrelated modules -- functools and importlib.resources._common, in different "
                 "fleet instances -- which is what argues this is interpreter-level rather than something about "
                 "one module. MECHANISM UNKNOWN, and two hypotheses were tested and killed: (a) a mishandled "
                 "thread-bootstrap allocation, since the session logs `Failed to create thread ...: MemoryError` "
                 "just before the abort -- but starting 4000 threads under the limit with 0-3000 MiB of ballast "
                 "produced no corruption on either interpreter; (b) libmpdec through cffi, since the reduction "
                 "builds huge Decimals -- but PyPy has no `_decimal` module at all, so that code takes the "
                 "pure-Python fallback and no foreign allocator is involved. A four-point cap sweep finds the "
                 "3072 window and MISSES the 1536 one entirely, which is the argument for sweeping finely.",
    ),
    dict(
        id="PYPY-FUZZ-010", slug="sigill-after-fork-from-thread",
        title="SIGILL in the child after `fork()` from a non-main thread, inside `threading._after_fork`",
        short="SIGILL after fork-from-a-thread",
        kind="sigill",
        sites=["lib/pypy3.11/_weakrefset.py:122 (discard)",
               "lib/pypy3.11/threading.py:1630 (_after_fork)",
               "lib/pypy3.11/multiprocessing/popen_fork.py:62 (_launch, its os.fork())"],
        repro="see repro.py -- concurrent multiprocessing.popen_fork.Popen() from worker threads",
        repro_file="repro.py",
        status="reproduced", reliability="12/12 on the original script, 3/12 on the 109-line reduction (a race)",
        needs_rlimit=True,
        reduced_from="11735-line generated script -> 109 lines",
        found_by=["fusil, fleet_05 and fleet_06 (broad stdlib)"],
        defect_class="crash-after-fork-from-thread",
        shared_with_cpython=False,
        cpython_behavior="clean, every run",
        prior_art="Unreported. The only SIGILL of the whole campaign, across six fleets.",
        leak_signature="Fatal Python error: Illegal instruction",
        analysis="`_launch` line 62 is its `os.fork()`. PyPy runs the after-fork hooks in the CHILD, so "
                 "`threading._after_fork()` executes there and dies walking a weakref set. The whole stack is "
                 "ordinary Python; an illegal instruction underneath it means either an RPython `ll_assert` "
                 "compiled to a trap or JIT-emitted code running in a state that no longer holds -- and forking "
                 "away from a multi-threaded, JIT-warm process is exactly such a state. The trigger includes "
                 "re-running `__init__` on an ALREADY-CONSTRUCTED Popen: the parent side of `_launch` succeeds "
                 "even when the argument is not a Process, because the child raises in `process_obj._bootstrap` "
                 "and `os._exit()`s, which the parent never sees. Three hand-written minimal attempts all failed "
                 "to reproduce it, including one that does exactly what the reduction does -- see the report.",
    ),
    dict(
        id="PYPY-FUZZ-011", slug="memoryview-pypy-raw-address-released",
        title="`memoryview._pypy_raw_address()` dereferences a RELEASED view where every sibling member raises",
        short="`_pypy_raw_address()` on a released view",
        kind="segv",
        sites=[],
        repro='m = memoryview(b""); m.release(); m._pypy_raw_address()',
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="fleet dirs -> 3 lines",
        found_by=["fusil, fleet_06 (broad stdlib, --test-private)"],
        defect_class="missing-sibling-guard",
        shared_with_cpython=False,
        cpython_behavior="no such method -- `_pypy_raw_address` is PyPy-only",
        prior_art="Unreported; no tracker issue mentions `_pypy_raw_address`. NOTE ON METHOD: an earlier "
                  "keyword search reported 'no prior art' for several findings in this catalog and was wrong, "
                  "because the relevant closed issues name different TYPES in their titles. This particular "
                  "claim was re-checked directly.",
        leak_signature="Segmentation fault",
        analysis="Measured over the whole public surface of `memoryview` on a released view, one member per "
                 "subprocess: 14 members raise `ValueError: operation forbidden on released memoryview object`, "
                 "3 (`c_contiguous`, `contiguous`, `f_contiguous`) return a value without checking, and exactly "
                 "one faults -- the one whose entire job is to hand back a raw pointer into the buffer. 1 of 19. "
                 "Reachable from idiomatic code, not only an explicit `.release()`: `memoryview` is a context "
                 "manager and `__exit__` releases, so the ordinary `with` form crashes identically. There is no "
                 "CPython differential to offer, so the argument is internal consistency -- which is the "
                 "stronger one: PyPy already decided what should happen here, implemented it 14 times, and "
                 "missed the 15th.",
    ),
    dict(
        id="PYPY-FUZZ-012", slug="format-syntaxerror-non-utf8-checkerror",
        title="Formatting a SyntaxError from non-UTF-8 source leaks an RPython `CheckError`",
        short="formatting a SyntaxError leaks CheckError",
        kind="systemerror-leak",
        sites=["implement_3.c:59620 (fastfunc_descr__format___2)",
               "pypy_objspace_std_8.c:58764 (Formatter_format_string)"],
        repro='import traceback\ntry:\n    compile(b"\\xff", b"\\x80", "exec")\nexcept SyntaxError as e:\n'
              '    traceback.format_exception(type(e), e, e.__traceback__)',
        repro_file="repro.py",
        status="reproduced", reliability="deterministic (6/6 rows on PyPy, 0/6 on CPython)",
        needs_rlimit=False,
        reduced_from="12748-line generated script -> 752 -> 53 lines -> 2 bytes",
        found_by=["fusil, fleet_06 (broad stdlib)"],
        defect_class="out-of-range-codepoint-from-invalid-utf8",
        shared_with_cpython=False,
        cpython_behavior="formats the same exception cleanly",
        prior_art="Unreported, but adjacent to TWO closed issues by this project's author. pypy#5111 "
                  "(`_string.formatter_field_name_split(b'\\xe1')`) leaked the SAME CheckError and is FIXED on "
                  "7.3.23 -- this path is a door the fix did not reach. pypy#5121 "
                  "(`logging._str_formatter.vformat(b'\\xff', ...)`) is also fixed. DISTINCT from the static "
                  "catalog's PYPYR-0004 (`format(0xD800,'c')`), verified side by side: different RPython "
                  "exception (OutOfRange vs CheckError), different guard, different entry point.",
        leak_signature="SystemError: unexpected internal exception (please report a bug): <CheckError object ...>",
        analysis="BOTH halves must be invalid UTF-8, and the conjunction is the whole trigger: the SOURCE must "
                 "be non-UTF-8 to produce the \"Non-UTF-8 code starting with ...\" SyntaxError, whose message "
                 "embeds the filename, and the FILENAME must be non-UTF-8 for that embedding to go wrong. It is "
                 "the FORMATTING that fails, not the compile -- `compile()` raises an ordinary SyntaxError and "
                 "the leak happens when anything renders it (`format_exception`, `print_exception`, or "
                 "`threading.excepthook` for an exception leaving a thread, which is how the fuzzer hit it). "
                 "Left unhandled, the same input prints the filename as `\\Uffffefa0`, which is not a codepoint: "
                 "`\\x80` should surrogate-escape to `\\udc80`. That out-of-range value is the same producer "
                 "behind PYPY-FUZZ-001 and 008, with a third consumer failing a third way -- fixing the producer "
                 "would likely close all three, whereas guarding each consumer would not.",
    ),
    dict(
        id="PYPY-FUZZ-013", slug="io-bufferedrwpair-uninitialized-segv",
        title="An uninitialized `_io.BufferedRWPair` segfaults through `.closed`, where every sibling type raises",
        short="uninitialized `BufferedRWPair`",
        kind="segv",
        sites=[],
        repro="import _io; _io.BufferedRWPair.__new__(_io.BufferedRWPair).closed",
        repro_file="repro.py",
        status="reproduced", reliability="deterministic",
        needs_rlimit=False,
        reduced_from="27 fleet dirs, all one signature -> 1 line",
        found_by=["fusil, fleet_07 (--new-uninit variant)"],
        defect_class="missing-sibling-guard",
        shared_with_cpython=False,
        cpython_behavior="RuntimeError: the BufferedRWPair object is being garbage-collected",
        prior_art="Unreported. Adjacent to two closed issues by this project's author -- pypy#5140 (StringIO "
                  "segfault after an invalid `__init__` reinitialization) and pypy#5126 (StringIO in an invalid "
                  "state) -- which are the SAME defect class on a different type. Both re-tested 2026-08-27 on "
                  "7.3.23: both FIXED. The fix did not propagate to BufferedRWPair.",
        leak_signature="Segmentation fault",
        analysis="`T.__new__(T)` builds an instance without running `__init__`, which is ordinary Python and "
                 "what pickle, copy and most deserializers do. Every other type in the family answers that state "
                 "with `ValueError: I/O operation on uninitialized object` -- BufferedRandom, BufferedReader, "
                 "BufferedWriter and TextIOWrapper all do. 1 of 8. `.closed` is the SINGLE ROOT: sweeping the "
                 "full surface splits it cleanly, with the seven faulting operations (`.closed`, `iter()`, "
                 "`list()`, for-loop, `.readlines()`, `.__enter__()`, `.isatty()`) all consulting `.closed` on "
                 "the way in, while the nine that check the underlying object directly all raise properly. That "
                 "makes it a one-line-shaped fix rather than a scattered family.",
    ),
    dict(
        id="PYPY-FUZZ-014", slug="hashlib-hmac-block-size-null-ctx",
        title="`_hashlib.HMAC.block_size` passes a NULL `ctx` to OpenSSL after a failed `__init__`",
        short="`HMAC.block_size` on a NULL ctx",
        kind="segv",
        sites=["lib/pypy3.11/_hashlib/__init__.py (HASH.__init__, sets self.ctx = ffi.NULL)",
               "lib/pypy3.11/_hashlib/__init__.py:241 (HMAC.block_size)"],
        repro="import _hashlib\nh = _hashlib.HMAC.__new__(_hashlib.HMAC)\ntry:\n    h.__init__(0)\n"
              "except Exception:\n    pass\nh.block_size",
        repro_file="repro.py",
        status="reproduced", reliability="deterministic (4/4 failing-construction cases)",
        needs_rlimit=False,
        reduced_from="13 fleet dirs, all one signature -> 4 lines",
        found_by=["fusil, fleet_07 (--new-uninit variant)"],
        defect_class="missing-sibling-guard",
        shared_with_cpython=False,
        cpython_behavior="CPython forbids constructing _hashlib.HMAC from Python at all (TypeError), so the "
                         "half-initialized state is unreachable there",
        prior_art="Unreported. Adjacent to pypy#5127 (`hashlib.shake_128()._keccak_init(())` aborting with "
                  "`free(): invalid next size (fast)`), filed by this project's author and closed; re-tested "
                  "2026-08-27 on 7.3.23: FIXED. The fix did not propagate to HMAC.block_size.",
        leak_signature="Segmentation fault (inside OpenSSL's HMAC_CTX_get_md)",
        analysis="The mechanism is visible in PyPy's own pure-Python source. `HASH.__init__` sets "
                 "`self.ctx = ffi.NULL` (twice -- a literally duplicated line), then `py_digest_by_name` raises "
                 "on an unknown digest name, leaving a LIVE object whose ctx is NULL. `HMAC.block_size` then "
                 "calls `lib.HMAC_CTX_get_md(self.ctx)` and only afterwards tests `if not md:` -- the check "
                 "guards the RESULT of the call, which is too late; the fault is inside the call. The object "
                 "survives its own failed constructor only because `__new__` plus an explicit `__init__` keeps "
                 "the reference -- a plain `_hashlib.HMAC('nosuchdigest')` also raises but drops the object. "
                 "The duplicated NULL assignment is worth pointing out on its own: someone was aware NULL is a "
                 "state this object passes through. Mirror image of PYPY-FUZZ-004 in the same cffi-stdlib "
                 "family: that assigns a DANGLING pointer after freeing, this assigns NULL and dereferences it.",
    ),
    dict(
        id="PYPY-FUZZ-015", slug="textio-shared-iterator-concurrent-next",
        title="Two threads calling `next()` on one file iterator segfault at EOF",
        short="concurrent next() on a shared file iterator",
        kind="segv",
        sites=[],
        repro='import threading\nf = open("/dev/null")\nit = iter(f)\n'
              'def w():\n    for _ in range(200):\n        try: next(it)\n'
              '        except Exception: pass\n'
              'ts = [threading.Thread(target=w) for _ in range(2)]\n'
              'for t in ts: t.start()\nfor t in ts: t.join()',
        repro_file="repro.py",
        status="reproduced",
        reliability="a race, so a rate rather than a verdict. Minimal 2-thread form: 3-6/6 "
                    "single runs depending on stream and machine load; wrapped in 20 rounds it "
                    "is 6/6 (CPython 0/6). The 335-line reduction is 11/12 single runs. Two "
                    "threads suffice; one thread is 0/4",
        needs_rlimit=False,
        reduced_from="1739-line generated script -> 335 lines (10/10) -> ~10 lines by hand",
        found_by=["fusil, fleet_08 (--concurrency-stress variant)"],
        defect_class="unsynchronised-text-layer-at-eof",
        shared_with_cpython=False,
        cpython_behavior="does not crash; concurrent iteration is unspecified there but raises "
                         "or returns interleaved lines",
        prior_art="Unreported.",
        leak_signature="Segmentation fault",
        analysis="Ordinary code -- `for line in f` shared between threads -- with no ctypes, no "
                 "address-space limit and no fuzzer scaffolding. TWO conditions are both "
                 "required, and neither reproduces alone. (1) The threads must actually EXHAUST "
                 "the iterator: a 5000-line file over 200 iterations is 0/6, the same file over "
                 "20000 iterations is 6/6, so the fault is at end-of-file rather than during "
                 "steady-state reading. (2) The stream must be the TEXT layer over a REAL file "
                 "descriptor: sys.__stdin__, open(...) and os.fdopen(...) all fault, while "
                 "io.TextIOWrapper(io.BytesIO(...)) (text layer, no fd) and "
                 "io.BufferedReader(io.FileIO(...)) (fd, no text layer) are both clean. That "
                 "split suggests the mechanism: PyPy releases the GIL around the real read() "
                 "syscall, so two threads can be inside TextIOWrapper.__next__ at once and race "
                 "its decoder/readahead state, where a BytesIO never releases the GIL and a "
                 "BufferedReader has no text-decoding state to corrupt. If that is right it is a "
                 "missing lock around the text layer's buffer, and the GIL -- which makes most "
                 "PyPy threading safe by accident -- is exactly what stops protecting it here. "
                 "Found by --concurrency-stress, a mode whose own generated scripts print "
                 "\"GIL enabled; running serialised\" and which was expected to find deadlocks "
                 "and re-entrancy rather than anything race-shaped.",
    ),
]
