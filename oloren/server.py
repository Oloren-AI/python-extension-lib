from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import json
import tempfile
import requests
import traceback
import threading
import io
import os
import inspect

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

CORS(app)

FUNCTIONS = {}


def register(name="", description="", num_outputs=1):
    def decorator(func):
        signature = inspect.signature(func)

        config = {
            "name": name if name != "" else func.__name__,
            "args": [],
            "operator": func.__name__,
            "num_outputs": num_outputs,
        }

        if description != "":
            config["description"] = description

        for param in signature.parameters.values():
            config["args"].append({"name": param.name, **param.annotation.config()})

        print(config)

        FUNCTIONS[func.__name__] = [func, config]

        return func

    return decorator


@app.route("/")
def health_check():
    return "OK"


@app.route("/ui/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/directory", methods=["GET"])
def get_directory():
    with open(os.path.join(os.path.dirname(__file__), "../frontend/config.json"), "r") as config_file:
        config = json.load(config_file)

    node = list(config["nodes"].keys())[0]

    return jsonify(
        {
            "nodes": [
                {
                    "module": node,
                    "scope": config["name"],
                    "url": "/ui/remoteEntry.js",
                    "metadata": function[1],
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
    print("Hello")
    try:
        # TODO: handle inputs in addition to simple body data

        inputs = body["node"]["data"]

        print(f"Node: {body['node']}")
        print(f"Inputs: {body['inputs']}")

        if "input_handles" in body["node"]:
            print("INPUT HANDLES", body["node"]["input_handles"])
            for input_idx, i in enumerate(sorted(body["node"]["input_handles"].keys())):
                inputs[int(i)] = body["inputs"][input_idx]
                print(f"INPUT {i} IS {body['inputs'][input_idx]}")

        outputs = FUNCTIONS[FUNCTION_NAME][0](*inputs)

        if isinstance(outputs, tuple):
            outputs = list(outputs)
        else:
            outputs = [outputs]

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

    print("OUTPUT IS ", outputs)
    try:
        files = {i: output for i, output in enumerate(outputs) if isinstance(output, io.BytesIO)}
        print(files)
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

        print("Outputs is ", outputs)
        print(response)
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


# Replace this with a loop over your FUNCTIONS
@app.route("/operator/<FUNCTION_NAME>", methods=["POST"])
def operator(FUNCTION_NAME):
    body = request.json
    body["node"]
    body["inputs"]
    body["id"]

    print("Received request for ", FUNCTION_NAME, " with body ", body)

    dispatcher_url = body.get("dispatcherurl") or f"http://{os.environ['DISPATCHER_URL']}"

    t = threading.Thread(target=execute_function, args=(dispatcher_url, body, FUNCTION_NAME))
    t.start()

    response = jsonify("Ok")
    response.status_code = 200
    return response


def run():
    print("Running server at port 4823!")
    app.run(host="0.0.0.0", port=4823, debug=(os.getenv("MODE") != "PROD"))
