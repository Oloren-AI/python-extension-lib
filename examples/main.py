import oloren as olo
import pandas as pd


@olo.register(description="Basic math operations on two numbers.")
def operation(operation=olo.Choice(["Add", "Subtract", "Multiply", "Divide"]), a=olo.Num(), b=olo.Num()):
    if operation == "Add":
        return a + b
    elif operation == "Subtract":
        return a - b
    elif operation == "Multiply":
        return a * b
    elif operation == "Divide":
        return a / b

@olo.register()
def log_message_test(log_message=print):
    print(log_message)
    log_message("START TEST")
    for i in range(10):
        log_message(f"i = {i}")
    return "OK"
    

@olo.register()
def sample(a=olo.Option(olo.String()), b=olo.String()):
    return f"a = {a} b = {b}"


@olo.register()
def read_file(file=olo.File()):
    return file


olo.run("exampleextension")


def handler(event, context):
    return olo.handler(event, context)
