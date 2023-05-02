import oloren as olo


@olo.register(description="Basic math operations on two numbers.")
def operation(operation: olo.choice(["Add", "Subtract", "Multiply", "Divide"]), a: olo.num, b: olo.num):
    if operation == "Add":
        return a + b
    elif operation == "Subtract":
        return a - b
    elif operation == "Multiply":
        return a * b
    elif operation == "Divide":
        return a / b


@olo.register()
def number(num: olo.num):
    return num


if __name__ == "__main__":
    olo.run()
