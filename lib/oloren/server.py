from flask import Flask, Response, request, send_from_directory, jsonify
from flask_cors import CORS
import json
import tempfile
from .util import OutputFile
import requests
import traceback
import threading
import io
import os
import inspect
from dataclasses import asdict
from .types import NULL_VALUE, Type, Config, Ty, Option
from typing import Dict, Tuple, Callable

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

CORS(app)

FUNCTIONS: Dict[str, Tuple[Callable, Config]] = {}
EXTENSION_NAME = ""


def register(name="", description="", num_outputs=1):
    """Register a function as an extension.

    The generated server satisfies the Oloren Orchestrator Extension API specification.

    Include a call to this at the bottom of your entry script.

    Args:
        name (str): Defaults to the name of the function.
        description (Optional[str]): A description of the function.
        num_outputs (int): The number of outputs the function returns. Defaults to 1.

    Example::

        @olo.register(name="foo", description="Returns foo and bar", num_outputs=2)
        def fun():
            return "foo", "bar"
    """

    def decorator(func):
        signature = inspect.signature(func)

        config = Config(
            name=name if name != "" else func.__name__,
            args=[],
            operator=func.__name__,
            num_outputs=num_outputs,
            description=description if description != "" else None,
        )

        for param in signature.parameters.values():
            if isinstance(param.default, type):
                raise TypeError("Default values for parameters must be literals.")
            if not isinstance(param.default, Type):
                raise TypeError(f"Parameter {param.name} of function {func.__name__} has an invalid type.")

            if isinstance(param.default, Option):
                param.default._type = param.default.inner.__class__.__name__

            config.args.append(Ty(param.name, param.default, type=param.default.__class__.__name__))

        FUNCTIONS[func.__name__] = (func, config)

        return func

    return decorator


@app.route("/")
def health_check():
    return "OK"


@app.route("/ui/<path:path>")
def serve_static_files(path):
    if path.endswith("remoteEntry.js"):
        with open(os.path.join(app.static_folder, path), "r") as file:
            content = file.read()
            new_content = (
                content.replace("var EXTENSIONNAME;", f"var {EXTENSION_NAME};")
                .replace("EXTENSIONNAME = __webpack_exports__;", f"{EXTENSION_NAME} = __webpack_exports__;")
                .replace("EXTENSIONNAME=m", f"{EXTENSION_NAME}=m")  # for the built version
            )
        return Response(new_content, content_type="application/javascript")

    return send_from_directory(app.static_folder, path)


@app.route("/directory", methods=["GET"])
def get_directory():
    return jsonify(
        {
            "nodes": [
                {
                    "module": "Base Node",
                    "scope": EXTENSION_NAME,
                    "url": "/ui/remoteEntry.js",
                    "metadata": asdict(function[1]),
                }
                for name, function in FUNCTIONS.items()
            ]
        }
    )


def download_from_signed_url(signed_url):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(signed_url, stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
    return tmp_file.name


def execute_function(dispatcher_url, body, FUNCTION_NAME):
    cur_dir = os.getcwd()
    try:
        inputs = [inp["value"] for inp in body["node"]["data"]]

        if "input_handles" in body["node"]:
            for input_idx, i in enumerate(sorted(body["node"]["input_handles"].keys())):
                inputs[int(i)] = body["inputs"][input_idx]

        for i, input in enumerate(inputs):  # convert file inputs into file paths
            if FUNCTIONS[FUNCTION_NAME][1].args[i].type == "File":
                inputs[i] = download_from_signed_url(inputs[i]["url"])
            if input == NULL_VALUE:
                inputs[i] = None

        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)

            outputs = FUNCTIONS[FUNCTION_NAME][0](*inputs)

            if isinstance(outputs, tuple):
                outputs = list(outputs)
            else:
                outputs = [outputs]

            # Convert output files
            for i, output in enumerate(outputs):
                if isinstance(output, OutputFile):
                    with open(output.path, "rb") as file:
                        outputs[i] = io.BytesIO(file.read())

            files = {i: output for i, output in enumerate(outputs) if isinstance(output, io.BytesIO)}
            if len(files) > 0:
                form_data = {
                    "node": body["id"],
                    "output": json.dumps([output if not isinstance(output, io.BytesIO) else "" for output in outputs]),
                }

                files = {str(i): f for i, f in enumerate(outputs) if isinstance(f, io.BytesIO)}

                response = requests.post(f"{dispatcher_url}/node_finished_file", data=form_data, files=files)
            else:
                response = requests.post(
                    f"{dispatcher_url}/node_finished",
                    headers={"Content-Type": "application/json"},
                    json={"node": body["id"], "output": [output for output in outputs]},
                )

    except Exception:
        error_msg = traceback.format_exc()
        requests.post(
            f"{dispatcher_url}/node_error",
            headers={"Content-Type": "application/json"},
            json={
                "node": body["id"],
                "error": error_msg,
            },
        )
    finally:
        os.chdir(cur_dir)


# Replace this with a loop over your FUNCTIONS
@app.route("/operator/<FUNCTION_NAME>", methods=["POST"])
def operator(FUNCTION_NAME):
    body = request.json
    body["node"]
    body["inputs"]
    body["id"]

    dispatcher_url = body.get("dispatcherurl") or f"http://{os.environ['DISPATCHER_URL']}"

    t = threading.Thread(target=execute_function, args=(dispatcher_url, body, FUNCTION_NAME))
    t.start()

    response = jsonify("Ok")
    response.status_code = 200
    return response


def run(name: str, port=4823):
    """Runs the extension. Launches a HTTP server at the specified port for development and port 80 for production.

    The generated server satisfies the Oloren Orchestrator Extension API specification.

    Include a call to this at the bottom of your entry script.

    Args:
        name (str): A globally unique name for the extension. The name must be a valid javascript variable name.
        port (int): Optional port number for use in development.

    Example::

        if __name__ == "__main__":
            olo.run("sample_extension", port=5829)
    """

    global EXTENSION_NAME
    EXTENSION_NAME = name.replace(" ", "").replace("-", "_")
    port = 80 if os.getenv("MODE") == "PROD" else port
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("MODE") != "PROD"))


__all__ = ["register", "run"]
