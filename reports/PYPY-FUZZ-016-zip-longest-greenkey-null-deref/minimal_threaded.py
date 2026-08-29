import itertools, threading

z = itertools.zip_longest([1, 2, 3], "abc")

bar = threading.Barrier(2)
def w():
    bar.wait()
    list(z)

ts = [threading.Thread(target=w) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
print("survived")
