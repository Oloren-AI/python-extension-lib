from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import json
import tempfile
import requests
import traceback
import threading
import io
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

CORS(app)

FUNCTIONS = []

def register(func):
    FUNCTIONS.append(func)
    return func

@app.route("/")
def health_check():
    return "OK"

@app.route("/ui/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route("/directory", methods=["GET"])
def get_directory():
    with open("core/frontend/config.json", "r") as config_file:
        config = json.load(config_file)

    nodes = list(config["nodes"].keys())

    return jsonify({
        "nodes": [{"module": node, "scope": config["name"], "url": "/ui/remoteEntry.js"} for node in nodes],
        "operators": {func: f"/operator/{func}" for func in FUNCTIONS}
    })

def download_from_signed_url(signed_url):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(signed_url, stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
    return tmp_file.name

def execute_function(dispatcher_url, body, FUNCTION_NAME):
    try:
        outputs = FUNCTIONS[FUNCTION_NAME](body["node"], body["inputs"])
    except Exception as e:
        error_msg = traceback.format_exc()
        requests.post(f"{dispatcher_url}/node_error",
                      headers={"Content-Type": "application/json"},
                      json={
                          "node": body["id"],
                          "error": error_msg,
                      })

    print("OUTPUT IS ", outputs)
    try:
        files = {
            i: output
            for i, output in enumerate(outputs)
            if isinstance(output, io.BytesIO)
        }
        print(files)
        if len(files) > 0:
            form_data = {
                "node":  body["id"],
                "output": json.dumps([output if not isinstance(output, io.BytesIO) else "" for output in outputs ])
            }

            files = {
                str(i): f
                for i, f in enumerate(outputs)
                if isinstance(f, io.BytesIO)
            }

            response = requests.post(f"{dispatcher_url}/node_finished_file", data=form_data, files=files)
        else:
            response = requests.post(f"{dispatcher_url}/node_finished",
                            headers={"Content-Type": "application/json"},
                            json= {
                                "node": body["id"],
                                "output": [output for output in outputs]},
                )

        print(f"Outputs is ", outputs)
        print(response)
    except Exception as e:
        error_msg = traceback.format_exc()
        requests.post(f"{dispatcher_url}/node_error",
                      headers={"Content-Type": "application/json"},
                      json={
                            "node": body["id"],
                            "error": error_msg,
                      })

# Replace this with a loop over your FUNCTIONS
@app.route(f"/operator/<FUNCTION_NAME>", methods=["POST"])
def operator(FUNCTION_NAME):
    body = request.json
    node = body["node"]
    inputs = body["inputs"]
    id = body["id"]

    dispatcher_url = body.get("dispatcherurl") or f"http://{os.environ['DISPATCHER_URL']}"

    t = threading.Thread(target=execute_function, args=(dispatcher_url, body, FUNCTION_NAME))
    t.start()

    response = jsonify("Ok")
    response.status_code = 200
    return response


def run():
    print("Running server at port 80!")
    app.run(host="0.0.0.0", port=80, debug=(os.getenv("MODE") != "PROD"))