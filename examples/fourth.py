import oloren as olo
import pandas as pd


@olo.register(description="Handle Directory input")
def hello_world(input_dir=olo.Dir()):
    import os
    return os.listdir(input_dir)

if __name__ == "__main__":
    olo.run("fourthextension", port=5002)
