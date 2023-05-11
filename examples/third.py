import oloren as olo
import pandas as pd


@olo.register(description="Handle JSON input")
def hello_world(input_json=olo.Json()):
    return input_json


if __name__ == "__main__":
    olo.run("thirdextension", port=5002)
