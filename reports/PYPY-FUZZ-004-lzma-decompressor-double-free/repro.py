"""PyPy 3.11 (7.3.23): double free in lzma.LZMADecompressor's input-buffer management.

    $ pypy3.11 repro.py      # -> free(): double free detected in tcache 2   (SIGABRT, 3/3)

TWO independent defects in lib/pypy3.11/_lzma.py, both in the hand-rolled malloc/free
buffer management. CPython's LZMADecompressor exposes only
check/decompress/eof/needs_input/unused_data; PyPy additionally exposes _bufsiz,
_decompress, _input_buffer, _input_buffer_size, lzs, lock, clear_input_buffer,
post_decompress_avail_data and pre_decompress_left_data, so all of this is reachable from
pure Python.

(1) THE TYPO -- post_decompress_avail_data, _lzma.py:562

        if self._input_buffer is not ffi.NULL and \
           self._input_buffer_size < lzs.avail_in:
            m.free(self._input_buffer)
            self._input_buffer = ffi.NONE          # <-- ffi.NONE does not exist

    `ffi.NONE` is not an attribute of cffi's FFI (verified: hasattr(ffi, 'NONE') is False).
    So the buffer is freed and then the assignment raises AttributeError, leaving
    self._input_buffer pointing at FREED memory. The very next statement is
    `if self._input_buffer is ffi.NULL:` -- the branch that would reallocate -- which would
    also never fire, confirming ffi.NULL was intended.

    Any later free of that stale pointer (clear_input_buffer, or another
    post_decompress_avail_data) is a DOUBLE FREE. Single-threaded and deterministic; this
    is what the script below demonstrates.

(2) THE RACE -- clear_input_buffer, _lzma.py:575

        def clear_input_buffer(self):
            if self._input_buffer is not ffi.NULL:
                m.free(self._input_buffer)
                self._input_buffer = ffi.NULL

    Check-then-act with no locking: two threads both pass the NULL test and both free.
    The class HAS a self.lock and decompress() uses it (`with self.lock:` at :595, which is
    what makes the INTERNAL calls at :618/:631 safe) -- this public entry point just does
    not take it. Reproduced separately: 8 threads x 200 iterations aborts with
    "double free or corruption (!prev)". This is the form the fuzzer hit first.

Suggested fix: `ffi.NONE` -> `ffi.NULL`, and take `self.lock` in clear_input_buffer (and in
post_decompress_avail_data / pre_decompress_left_data, which are equally exposed and equally
unlocked).

Related but distinct: pypy#5330 (open) reports a memory LEAK in lzma decompression, same
file and same buffer machinery, different symptom.

Found by fusil against PyPy 3.11.15 / PyPy 7.3.23 (linux x86_64).
"""

import lzma
import sys

from _lzma import ffi


def main():
    print("%s %s" % (sys.implementation.name, sys.version.split()[0]))
    print("ffi.NONE exists:", hasattr(ffi, "NONE"), "(the typo at _lzma.py:562)")

    blob = lzma.compress(bytes(range(256)) * 400)
    decompressor = lzma.LZMADecompressor()

    # Feed the stream in small chunks with a tiny max_length so unconsumed input is saved
    # into _input_buffer via the normal, locked path.
    for offset in range(0, 200, 7):
        decompressor.decompress(blob[offset : offset + 7], max_length=1)

    buffer_before = decompressor._input_buffer
    print("input buffer allocated:", buffer_before,
          "size:", decompressor._input_buffer_size)
    assert buffer_before != ffi.NULL, "setup failed: no input buffer was allocated"

    # Take the free branch: _input_buffer_size < lzs.avail_in.
    decompressor.lzs.avail_in = decompressor._input_buffer_size + 1
    try:
        decompressor.post_decompress_avail_data()
    except AttributeError as exc:
        print("post_decompress_avail_data ->", type(exc).__name__, ":", exc)

    print("buffer AFTER the free branch:", decompressor._input_buffer)
    print("  same pointer as before the free:",
          decompressor._input_buffer == buffer_before)
    print("  is it ffi.NULL (as intended)? ", decompressor._input_buffer == ffi.NULL)

    print("\ncalling clear_input_buffer() -- frees that stale pointer again ...", flush=True)
    decompressor.clear_input_buffer()

    print("!! survived -- this PyPy appears to be fixed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
