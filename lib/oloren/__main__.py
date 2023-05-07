"""
Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
"""

import sys
import os
import argparse
import subprocess
import inspect


def handler(event, context):
    import oloren

    oloren.handler(event, context)


def run():
    app_root = os.getcwd()

    parser = argparse.ArgumentParser(prog="Runs oloren application", description="oloren application runner")

    parser.add_argument("script", type=str, help="Path to the script to run")

    args = parser.parse_args()

    print(f"Running {args.script}... in {app_root}")

    if "MODE" in os.environ and os.environ["MODE"] == "LAMBDABUILD":
        handler_source = inspect.getsource(handler)
        with open(args.script, "a") as f:
            f.write("\n" + handler_source)
    elif "MODE" in os.environ and os.environ["MODE"] == "LAMBDA":
        subprocess.run([sys.executable, "-m", "awslambdaric", args.script.replace(".py", "handler")], cwd=app_root)
    else:
        subprocess.run([sys.executable, args.script], cwd=app_root)


def main():
    run()


if __name__ == "__main__":
    main()
