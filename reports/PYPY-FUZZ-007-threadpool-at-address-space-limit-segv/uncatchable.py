# PYPY-FUZZ-007 is UNCATCHABLE -- it is a hard SIGSEGV inside construction, not an
# exception and not a __del__/teardown fault.
#
#   $ (ulimit -v 524288; pypy3.11 uncatchable.py)
#
# In 6 of 8 runs here, NOTHING is printed: neither the `CAUGHT` line nor
# `SURVIVED-CONSTRUCTION`. The process is gone before the except clause can run.
import faulthandler
faulthandler.enable()
import multiprocessing.dummy

try:
    multiprocessing.dummy.Pool()
except BaseException as exc:
    print("CAUGHT:", type(exc).__name__, exc, flush=True)
print("SURVIVED-CONSTRUCTION", flush=True)
import gc
gc.collect()
print("SURVIVED-GC", flush=True)
