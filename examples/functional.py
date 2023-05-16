import oloren as olo


@olo.register()
def add_one(num=olo.Num()):
    print(f"Num has value: {num}")
    return num + 1


@olo.register()
def num_list():
    return [1, 2, 3, 4, 5]


@olo.register()
def map(lst=olo.String(), fn=olo.Func()):
    return [fn(num) for num in lst]


olo.run("functional")
