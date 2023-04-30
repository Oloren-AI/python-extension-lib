import oloren as olo

@olo.register()
def operation(operation: olo.choice(["Add", "Subtract", "Multiply", "Divide"]), a: olo.number, b: olo.number) -> olo.number:
    if operation == "Add":
        return a + b
    elif operation == "Subtract":
        return a - b
    elif operation == "Multiply":
        return a * b
    elif operation == "Divide":
        return a / b

if __name__ == "__main__":
    olo.run()