import oloren as olo


@olo.register()
def add_one(num=olo.Num(), num2=olo.Num(), log_message=print):
    log_message(f"Adding one to: {num}")
    return num + num2


@olo.register()
def num_list():
    return list(range(50))


import threading


@olo.register()
def map(lst=olo.Json(), fn=olo.Func(), map=None):
    return olo.map([[x, 1] for x in lst], fn, batch_size=None)


olo.run("functional")
