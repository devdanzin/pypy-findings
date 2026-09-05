# CONTROL for PYPY-FUZZ-007: is this just "PyPy dies when a thread cannot start"?
#
#   $ (ulimit -v 524288; pypy3.11 control_bare_threads.py)
#
# No. Starting live threads until the address space is exhausted raises
# `RuntimeError: can't start new thread` cleanly on BOTH PyPy 7.3.23 and CPython 3.14.
# So the defect is NOT in thread bootstrap; it is specific to the pool-construction
# path -- `Pool._repopulate_pool_static`'s `w.start()` loop (pool.py:314).
import faulthandler
faulthandler.enable()
import threading

ev = threading.Event()      # keep every thread alive so the stacks accumulate
threads = []
for _ in range(4096):
    t = threading.Thread(target=ev.wait)
    t.start()
    threads.append(t)
print("started all", flush=True)
