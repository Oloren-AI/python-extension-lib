from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import json
import tempfile
import requests
import random
import traceback
import threading
from urllib.parse import urlparse

from functions import FUNCTIONS


# set directory to root of project

import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))


# Import your utility functions and FUNCTIONS here
# from util import FlowNodeData, Json, fileSchema, runGraph, FUNCTIONS

app = Flask(__name__, static_folder=os.path.join(root_dir, "core/frontend/dist"))

CORS(app)

@app.route("/")
def health_check():
    return "OK"

@app.route("/ui/<path:path>")
def serve_static_files(path):
    print("SERVING STATIC FILES, ASKING FOR ", path)
    return send_from_directory(app.static_folder, path)

@app.route("/directory", methods=["GET"])
def get_directory():
    hostname = request.headers.get("X-Forwarded-Host") or request.headers.get("Host")
    print("DIRECTORY CALLED ")
    print(os.getcwd())

    with open(os.path.join(root_dir,"core/frontend/config.json"), "r") as config_file:
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
    print("EXECUTING FUNCTION ", FUNCTION_NAME)
    print("FUNCTIONS ARE ", FUNCTIONS)
    try:
        output = FUNCTIONS[FUNCTION_NAME](body["node"], body["inputs"])
        requests.post(f"{dispatcher_url}/node_finished",
                    headers={"Content-Type": "application/json"},
                    json= {
                        "node": body["id"],
                        "output": output}
        )
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

if __name__ == "__main__":

    node_env = os.getenv('NODE_ENV')

    def save_port_to_file(port):
        print('Saving port to file. Port:', port)
        with open('.port', 'w') as f:
            f.write(str(port))

    def read_port_from_file():
        try:
            with open('.port', 'r') as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    if node_env == 'production':
        print(f"Running at URL http://localhost:80")
        app.run(host='0.0.0.0', port=80)
    else:
        port = read_port_from_file()
        if port == 0:
            port = random.randint(1024, 65535)
            print('Assigning random available port.')

        print('Launching port at', port)
        print('Running at URL http://localhost:' + str(port))
        save_port_to_file(port)
        app.run(host='0.0.0.0', port=port, debug=True)
