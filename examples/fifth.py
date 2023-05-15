import oloren as olo
import pandas as pd


@olo.register(description="Handle functions")
def map(input_list = olo.Json(), func = olo.Func()):
    print(input_list)
    print(func)
    results = []
    for item in input_list:
        results.append(func(item))
        print(results)
    return input_list

if __name__ == "__main__":
    olo.run("fifthextension", port=5002)
