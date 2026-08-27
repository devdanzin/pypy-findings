import gc, weakref
class D:
    def __del__(self): pass
def make():
    a = D(); b = D(); a.o = b; b.o = a; return a
keep = []
try:
    while True:
        keep.append(make())
except MemoryError:
    pass
for _ in range(30):
    gc.collect()
print("survived")
