from dataclasses import dataclass


@dataclass
class OutputFile:
    """
    A class for defining a file output of your hook.

    Our library will automatically find the file and upload it for you to the Orchestrator backend.

    Args:
        path (str): The path for the file.

    Example::

        @olo.register(description="Get the head of a CSV file.")
        def head(csv_file=olo.File(), rows=olo.Num()):
            pd.read_csv(csv_file).head(rows).to_csv("head.csv")
            return olo.OutputFile("head.csv")
    """

    path: str
