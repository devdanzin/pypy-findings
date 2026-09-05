import faulthandler; faulthandler.enable()
_ballast = [bytearray(1024 * 1024) for _ in range(400)]
import multiprocessing.pool
for _ in range(3):
    multiprocessing.pool.ThreadPool()
