import threading

for _ in range(20):                      # a race: loop so one run is enough to see it
    f = open("/dev/null")
    it = iter(f)

    def worker():
        for _ in range(200):
            try:
                next(it)
            except Exception:
                pass

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

print("survived")
