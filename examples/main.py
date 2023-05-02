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


@olo.register(description="Convert CSV file to JSON")
def dataframe_to_json(csv_file=olo.File()):
    return pd.read_csv(csv_file).to_json()


@olo.register(num_outputs=2)
def twooutputs(s=olo.String(), num=olo.Num()):
    return s, num


@olo.register()
def number(num=olo.Num()):
    return num


@olo.register()
def string(s=olo.String()):
    return s


if __name__ == "__main__":
    olo.run("raunakextension")
