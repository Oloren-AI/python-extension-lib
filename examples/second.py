import oloren as olo
import pandas as pd


@olo.register(description="Convert CSV file to JSON")
def hello_world(csv_file=olo.File()):
    return pd.read_csv(csv_file).to_json()


if __name__ == "__main__":
    olo.run("secondextension", port=5002)
