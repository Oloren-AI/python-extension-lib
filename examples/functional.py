import oloren as olo


@olo.register()
def add_one(num=olo.Num(), log_message=print):
    log_message(f"Adding one to: {num}")
    return num + 1


@olo.register()
def num_list():
    return list(range(50))


import threading


@olo.register()
def map(lst=olo.String(), fn=olo.Func()):
    results = [None] * len(lst)
    lock = threading.Lock()

    def map_thread(i):
        result = fn(lst[i])
        with lock:
            results[i] = result

    threads = []
    for i in range(len(lst)):
        thread = threading.Thread(target=map_thread, args=(i,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return results


olo.run("functional")
