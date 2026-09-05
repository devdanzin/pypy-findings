# PyPy 3.11 (7.3.23): SIGSEGV constructing a ThreadPool near an address-space limit.
#
#   $ (ulimit -v 524288; pypy3.11 minimal.py)     # 6/8 SIGSEGV here
#
# No ballast: PyPy's own startup already puts the process in the band at a 512 MiB
# RLIMIT_AS, so the bare call is enough. `minimal_ballast.py` is the older form that
# allocates the band by hand -- keep it, because the band's position moves between
# machines and `repro.py` sweeps for it.
#
# CPython raises `RuntimeError: can't start new thread` here instead, 6/6 at every limit
# from 1024 MiB down to 128 MiB.
import faulthandler
faulthandler.enable()
import multiprocessing.dummy
multiprocessing.dummy.Pool()
