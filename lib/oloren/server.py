from flask import Flask, Response, request, send_from_directory, jsonify, session
from flask_cors import CORS
import json
import tempfile
import time
import uuid
from .util import OutputFile
import requests
import traceback
import threading
import io
import os
import copy
import inspect
from dataclasses import asdict
from .types import NULL_VALUE, Type, Config, Ty, Option
from typing import Dict, Tuple, Callable, Union, List
import subprocess
import sys
import zipfile
import socketio
import asyncio
from functools import partial

from contextlib import contextmanager

DISPATCHER_URL = None
TOKEN = None

def set_vars(dispatcher_url, token):
    global DISPATCHER_URL
    global TOKEN
    DISPATCHER_URL = dispatcher_url
    TOKEN = token

@contextmanager
def change_dir(destination):
    try:
        cwd = os.getcwd()  # get current directory
        os.chdir(destination)  # change directory
        yield
    finally:
        os.chdir(cwd)  # change back to original directory


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.secret_key = "catcocacolacatdog"
CORS(app)

session = requests.Session()

FUNCTIONS: Dict[str, Tuple[Callable, Config]] = {}
EXTENSION_NAME = ""

_RESERVED_BATCH_KEY = "RESERVED_OLOREN_KEYWORD_BATCH"


def post_log_message(dispatcher_url, myUuid, progressId, level, message):
    print("POSTING LOG MESSAGE to PROGRESS")
    response = requests.post(
        f"{dispatcher_url}/node_progress",
        headers={"Content-Type": "application/json"},
        json={
            "progressId": progressId,
            "level": level,
            "type": "message",
            "data": {"message": message},
            "uuid": myUuid,
        },
    )

    print(f"LOG: {message}")
    print(f"log message response: {response.status_code} {response.text}")


def log_message(dispatcher_url, myUuid, progressId, level, message):
    log_thread = threading.Thread(target=post_log_message, args=(dispatcher_url, myUuid, progressId, level, message))
    log_thread.start()
    print("Done logging message")


def get_log_message_function(dispatcher_url, myUuid):
    def log(*messages, sep="", level=1):
        log_message(dispatcher_url, myUuid, str(uuid.uuid4()), level, sep.join([str(x) for x in messages]))

    return log


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
            name=name if name != "" else func.__name__.replace("_", " ").title(),
            args=[],
            operator=func.__name__,
            num_outputs=num_outputs,
            description=description if description != "" else None,
        )

        log_message_on = False
        for param_key, param in zip(signature.parameters.keys(), signature.parameters.values()):
            if param_key == "log_message":
                log_message_on = True
                continue
            if param_key == "map":
                continue
            if isinstance(param.default, type):
                raise TypeError("Default values for parameters must be literals.")
            if not isinstance(param.default, Type):
                raise TypeError(f"Parameter {param.name} of function {func.__name__} has an invalid type.")

            if isinstance(param.default, Option):
                param.default._type = param.default.inner.__class__.__name__
                config.args.append(
                    Ty(param.name, param.default, type=param.default.__class__.__name__, default=param.default.default)
                )
            else:
                config.args.append(Ty(param.name, param.default, type=param.default.__class__.__name__, default=None))

        def wrappedFunc(*args, log_message=None, **kwargs):
            try:
                print(f"Running function {func.__name__}", flush=True)
                start_time = time.time()
                if log_message_on:
                    y = func(*args, log_message=log_message, **kwargs)
                else:
                    y = func(*args, **kwargs)
                end_time = time.time()
                print(f"Finished function {func.__name__} in {end_time - start_time} seconds", flush=True)
                return y
            except Exception as e:
                print(f"Error in function {func.__name__}: {e}")
                traceback.print_exc()
                raise e

        FUNCTIONS[func.__name__] = (wrappedFunc, config)

        return func

    return decorator


import socketio
import requests
import json
from typing import List, Union
import uuid
from threading import Timer


@app.route("/")
def health_check():
    return "OK"


def replace_last_instance(text, word_to_replace, replacement):
    index = text.rfind(word_to_replace)
    if index != -1:
        return text[:index] + replacement + text[index + len(word_to_replace) :]
    return text


def process_remoteentry(path):
    with open(os.path.join(app.static_folder, path), "r") as file:
        content = file.read()
        new_content = content.replace("var EXTENSIONNAME;", f"var {EXTENSION_NAME};")
        new_content = replace_last_instance(new_content, "EXTENSIONNAME", EXTENSION_NAME)
    return new_content


@app.route("/ui/<path:path>")
def serve_static_files(path):
    if path.endswith("remoteEntry.js"):
        new_content = process_remoteentry(path)
        return Response(new_content, content_type="application/javascript")

    return send_from_directory(app.static_folder, path)


def get_directory_json():
    return {
        "nodes": [
            {
                "module": "Base Node",
                "scope": EXTENSION_NAME,
                "url": "/ui/remoteEntry.js",
                "metadata": {**asdict(function[1]), **{"path": "value"}},
            }
            for name, function in FUNCTIONS.items()
        ]
    }


@app.route("/directory", methods=["GET"])
def get_directory():
    return jsonify(get_directory_json())


from functools import wraps
import errno
import os
import signal


class TimeoutError(Exception):
    pass


def timeout(seconds=100, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


import uuid


def connect_to_socket(dispatcher_url, max_retries=3, wait_timeout=10):
    socket_url = dispatcher_url.replace("http://", "ws://").replace("https://", "wss://")

    socket = socketio.Client()

    retries = 0
    while retries <= max_retries:
        try:
            socket.connect(socket_url, wait_timeout=wait_timeout)
            print("Connected successfully.")
            return socket
        except Exception as e:
            print(f"Exception occurred: {e}")
            retries += 1
            wait = 2**retries  # exponential backoff
            print(f"Retrying in {wait} seconds.")
            time.sleep(wait)

    print(f"Failed to connect after {max_retries} retries.")
    return None


import random


class SocketManager:
    def __init__(self):
        self.connections = {}

    def get_connection(self, client_uuid, dispatcher_url, node_id, after_connect_callback=None):
        """Creates connection if it doesn't exist, otherwise returns existing connection

        Returns:
        (socketio.Client, uuid)
        """

        if client_uuid not in self.connections:
            blue_node_uuid = str(uuid.uuid4())
            socket = connect_to_socket(dispatcher_url)
            socket.emit(
                "extensionregister",
                data={"uuid": blue_node_uuid, "node_id": node_id},
                callback=lambda *args: after_connect_callback(blue_node_uuid),
            )

            self.connections[client_uuid] = (socket, blue_node_uuid)

            return socket

        socket, blue_node_uuid = self.connections[client_uuid]
        if after_connect_callback is not None:
            after_connect_callback(blue_node_uuid)
        return socket


_RESERVED_INPUT_KEY = "INITIALIZE_SOCKET_RESERVED_ORCHESTRATOR_INPUT"

manager = SocketManager()


def run_blue_node(
    graph, node_id, dispatcher_url, inputs, client_uuid, uid=None, token=None, timeout=15 * 60 * 200, retries=3
):
    if retries == 0:
        raise Exception("Failed to run blue node")
    try:
        if len(inputs) == 1 and inputs[0] == _RESERVED_INPUT_KEY:
            finished = False

            def wait_finished(*args):
                nonlocal finished
                finished = True

            socket = manager.get_connection(client_uuid, dispatcher_url, node_id, after_connect_callback=wait_finished)

            while True:
                if finished:
                    return
                time.sleep(0.005)

        assert (
            token is not None
        ), "Token must be provided, you likely need to assign the permission 'Run Graph Access` via the Extensions window"

        maxId = max([outputId["id"] for outputId in graph["output_ids"]]) + 1
        if not uid:
            uid = str(uuid.uuid4())

        newElements = [
            {
                "id": f"{uid}-input-{idx}",
                "data": inp,
                "operator": "extractdata",
                "input_ids": [],
                "output_ids": [{"id": maxId + idx}],
            }
            for idx, inp in enumerate(inputs)
        ]

        newGraph = [graph] + newElements
        newGraph = json.loads(json.dumps(newGraph))
        newGraph[0]["id"] = f"{uid}-graph"
        newGraph[0]["input_ids"] = [el["output_ids"][0] for el in newElements]

        output = None
        error = None

        start_time = time.time()

        def on_extensionregister_response(blue_node_uuid):
            response = requests.post(
                f"{dispatcher_url}/run_graph",
                data=json.dumps({"graph": newGraph, "uuid": blue_node_uuid}),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            )

            if response.status_code != 200:
                raise Exception(response.text)
            else:
                print(f"Successfully started graph {uid} in {time.time() - start_time} seconds")

        socket = manager.get_connection(
            client_uuid, dispatcher_url, node_id, after_connect_callback=on_extensionregister_response
        )

        @socket.on("node")
        def node(node_data):
            nonlocal output, error
            if f"{uid}-graph" == node_data["data"]["id"]:
                if node_data["status"] == "finished":
                    if len(node_data["data"]["output_ids"]) > 0:
                        output = node_data["output"]
                elif node_data["status"] != "running":
                    print("Received error on ", node_data["data"]["id"])
                    error = json.dumps(node_data)

        timeout_counter = timeout
        while True:
            if timeout_counter <= 0:
                raise Exception("Timeout")
            if output is not None:
                return output
            if error is not None:
                raise Exception(error)
            time.sleep(0.005)
            timeout_counter -= 1

    except Exception as e:
        print(f"Exception occurred: {e}")
        return run_blue_node(
            graph,
            node_id,
            dispatcher_url,
            inputs,
            client_uuid,
            uid=uid,
            token=token,
            timeout=timeout,
            retries=retries - 1,
        )


from multiprocessing import Process, Manager


@app.route("/operator/<FUNCTION_NAME>", methods=["POST"])
def operator(FUNCTION_NAME):
    start_dir = os.getcwd()
    print("Starting in directory: ", start_dir)
    try:
        body = request.json
        body["node"]
        body["inputs"]
        body["id"]

        DISPATCHER_URL = body.get("dispatcherurl") or f"http://{os.environ['DISPATCHER_URL']}"

        p = Process(target=execute_function, args=(DISPATCHER_URL, body, FUNCTION_NAME))
        p.start()

        response = jsonify("Ok")
        response.status_code = 200
        print("Returning response")
        return response
    except Exception:
        error_msg = traceback.format_exc()
        requests.post(
            f"{DISPATCHER_URL}/node_error",
            headers={"Content-Type": "application/json"},
            json={
                "node": body["id"],
                "error": error_msg,
            },
        )
        print("Returning error")
        return error_msg, 500


def download_from_signed_url(signed_url):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(signed_url, stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
    return tmp_file.name

def download_from_file_record(record):
    purl = requests.post(
        f"{DISPATCHER_URL}/get_purl",
            data=json.dumps({"files": [record]}),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"},
        )
    print(purl)
    return download_from_signed_url(purl.json()[0]["url"])

def download_from_registered_file(path):
    purl = requests.post(
        f"{DISPATCHER_URL}/get_registered_purl",
            data=json.dumps({"path": path}),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"},
    )

    return download_from_file_record(purl.json()[0]['fileInfo'])

def execute_function(dispatcher_url, body, FUNCTION_NAME):
    print("Execute function called")
    DISPATCHER_URL = dispatcher_url
    TOKEN = body["node"]["token"]

    all_func = {}

    def my_run_graph(*args, graph=None, timeout=15*60*200):
        return run_blue_node(graph, body["id"], DISPATCHER_URL, args, body["uuid"], token=TOKEN, timeout = timeout)

    try:
        inputs = [inp["value"] for inp in body["node"]["data"]]

        if "input_handles" in body["node"]:
            for input_idx, i in enumerate(sorted(body["node"]["input_handles"].keys())):
                inputs[int(i)] = body["inputs"][input_idx]

        for i, input in enumerate(inputs):  # convert file inputs into file paths
            if FUNCTIONS[FUNCTION_NAME][1].args[i].type == "File":
                assert (
                    isinstance(input, dict) and "url" in input
                ), "File inputs must be signed URLs. The error is most likely caused by mapping a non-file input to a file input."
                inputs[i] = download_from_signed_url(inputs[i]["url"])
            elif FUNCTIONS[FUNCTION_NAME][1].args[i].type == "Dir":
                assert (
                    isinstance(input, dict) and "url" in input
                ), "Directory inputs must be signed URLs. The error is most likely caused by mapping a non-directory input to a directory input."
                inputs[i] = download_from_signed_url(inputs[i]["url"])
                os.rename(inputs[i], inputs[i] + ".zip")
                with zipfile.ZipFile(inputs[i] + ".zip", "r") as zip_ref:
                    zip_ref.extractall(inputs[i])
            elif FUNCTIONS[FUNCTION_NAME][1].args[i].type == "Func":
                input_graph = copy.deepcopy(inputs[i])

                # all_func[i] = partial(my_run_graph, graph=input_graph)
                # inputs[i] = all_func[i]
                inputs[i] = partial(my_run_graph, graph=input_graph)
            elif FUNCTIONS[FUNCTION_NAME][1].args[i].type == "Funcs":
                input_graphs = copy.deepcopy(inputs[i])

                my_funcs = {}
                for j in range(len(input_graphs)):
                    my_funcs[j] = partial(my_run_graph, graph=input_graphs[j])

                inputs[i] = my_funcs

            # print(f"Input: {input}")
            # print(f"Func input type: {FUNCTIONS[FUNCTION_NAME][1].args[i].type}")
            # print(f"Func input default: {FUNCTIONS[FUNCTION_NAME][1].args[i].default}")
            # print(f"Function arg: {FUNCTIONS[FUNCTION_NAME][1].args[i]}")
            if input == NULL_VALUE:
                if (
                    FUNCTIONS[FUNCTION_NAME][1].args[i].type == "Option"
                    and FUNCTIONS[FUNCTION_NAME][1].args[i].ty._type == "Bool"
                    and FUNCTIONS[FUNCTION_NAME][1].args[i].default is None
                ):
                    inputs[i] = False
                else:
                    inputs[i] = FUNCTIONS[FUNCTION_NAME][1].args[i].default
        cur_dir = os.getcwd()
        print("Current directory: ", cur_dir)
        with tempfile.TemporaryDirectory() as tmp_dir:
            with change_dir(tmp_dir):
                # print(f"Running {FUNCTION_NAME} with body {body}")
                log_message_func = get_log_message_function(DISPATCHER_URL, body["uuid"])
                # print(f"Log message function: {log_message_func}")

                if (
                    len(inputs) > 0
                    and sum(
                        [
                            inputs[i][0] == _RESERVED_BATCH_KEY if type(inputs[i]) == list and len(inputs[i]) > 0 else 0
                            for i in range(len(inputs))
                        ]
                    )
                    == 1
                ):
                    batch_idx = [i for i in range(len(inputs)) if inputs[i][0] == _RESERVED_BATCH_KEY][0]
                    outputs = [
                        _RESERVED_BATCH_KEY,
                        [
                            FUNCTIONS[FUNCTION_NAME][0](
                                *(inputs[:i] + batch + inputs[i + 1 :]), log_message=log_message_func
                            )
                            for batch in inputs[batch_idx][1]
                        ],
                    ]
                elif len(inputs) > 0 and sum(
                    [
                        inputs[i][0] == _RESERVED_BATCH_KEY if type(inputs[i]) == list and len(inputs[i]) > 0 else 0
                        for i in range(len(inputs))
                    ]
                ) == len(inputs):
                    outputs = [
                        _RESERVED_BATCH_KEY,
                        [
                            FUNCTIONS[FUNCTION_NAME][0](*batch, log_message=log_message_func)
                            for batch in zip(*[inp[1] for inp in inputs])
                        ],
                    ]
                else:
                    outputs = FUNCTIONS[FUNCTION_NAME][0](*inputs, log_message=log_message_func)
                print("Done running function with outputs: ", outputs)
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
                        "output": json.dumps(
                            [output if not isinstance(output, io.BytesIO) else "" for output in outputs]
                        ),
                    }

                    files = {str(i): f for i, f in enumerate(outputs) if isinstance(f, io.BytesIO)}

                    response = requests.post(f"{DISPATCHER_URL}/node_finished_file", data=form_data, files=files)

                    if response.status_code != 200:
                        print(f"Failed to call node_finished_file on finish: {response.text}")
                        raise Exception(f"Failed to call node_finished_file on finish: {response.text}")
                else:
                    response = requests.post(
                        f"{DISPATCHER_URL}/node_finished",
                        headers={"Content-Type": "application/json"},
                        json={"node": body["id"], "output": [output for output in outputs]},
                    )

                    if response.status_code != 200:
                        print(f"Failed to call node_finished on finish: {response.text}")
                        raise Exception(f"Failed to call node_finished on finish: {response.text}")
    except Exception:
        error_msg = traceback.format_exc()
        print("Posting error: ", error_msg)
        response = requests.post(
            f"{DISPATCHER_URL}/node_error",
            headers={"Content-Type": "application/json"},
            json={
                "node": body["id"],
                "error": error_msg,
            },
        )
        print(f"Posting error response, status code: {response.status_code}, text: {response.text}")
    print("Done execute function")


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

    # Some special stuff to handle deployment to AWS Lambda
    script = os.path.abspath(os.path.abspath(sys.argv[0]))
    if "MODE" in os.environ and os.environ["MODE"] == "LAMBDABUILD":
        handler_source = """
def handler(event, context):
    import oloren
    oloren.handler(event, context)
"""
        # Check if the handler already exists
        with open(script, "r") as f:
            if handler_source in f.read():
                return

        with open(script, "a") as f:
            f.write("\n" + handler_source)
        subprocess.run([sys.executable, "-m", "pip", "install", "awslambdaric"], timeout=900)
        return
    elif "MODE" in os.environ and os.environ["MODE"] == "JOB_RUN":
        # Load the inputs from environment variable
        body = json.loads(os.environ["body"])
        dispatcher_url = body.get("dispatcherurl")
        execute_function(dispatcher_url, body, body["node"]["metadata"]["operator"])
        return "ok"
    elif "MODE" in os.environ and os.environ["MODE"] == "LAMBDA":
        subprocess.run(
            [sys.executable, "-m", "awslambdaric", sys.argv[0].replace(".py", ".handler")], cwd=os.getcwd(), timeout=900
        )
        return

    global EXTENSION_NAME
    EXTENSION_NAME = name.replace(" ", "").replace("-", "_")

    if len(FUNCTIONS) == 0:
        raise ValueError("You must register at least one function with @olo.register.")

    if os.getenv("BUILDCOPY") is not None:
        print("Copying static files...")

        import shutil

        buildcopy = os.path.join(os.getenv("BUILDCOPY"), "ui")

        remote_entry_path = os.path.abspath(os.path.join(buildcopy, "remoteEntry.js"))
        directory_path = os.path.abspath(os.path.join(buildcopy, "../directory"))

        shutil.copytree(os.path.join(os.path.dirname(__file__), "static"), buildcopy)

        remote = process_remoteentry(remote_entry_path)
        with open(remote_entry_path, "w") as file:
            file.write(remote)

        with open(directory_path, "w") as file:
            file.write(json.dumps(get_directory_json()))

        print("Done.")
        return

    if os.getenv("MODE") == "LAMBDA":
        return

    port = 80 if os.getenv("MODE") == "PROD" else port

    app.run(host="0.0.0.0", port=port, debug=(os.getenv("MODE") != "PROD"))


def handler(event, context):
    """Handler for AWS Lambda.

    The handler will be automatically inserted in the main file when deploying to AWS Lambda.

    Args:
        event (dict): The event object.
        context (dict): The context object.

    Example::

        def handler(event, context):
            return olo.handler(event, context)
    """

    body = json.loads(event["body"])
    DISPATCHER_URL = body.get("dispatcherurl") or f"http://{os.environ['DISPATCHER_URL']}"

    execute_function(DISPATCHER_URL, body, body["node"]["metadata"]["operator"])

    return "Ok"


def print_message(message):
    pass


def upload_file(file_path):
    """
    This function uploads a file to Orchestrator and returns the file S3 json.
    """

    # Ensure the file exists
    try:
        with open(file_path, "rb") as f:
            pass
    except FileNotFoundError:
        print(f"No file found at path: {file_path}")
        return

    # Open the file in binary mode and upload it
    with open(file_path, "rb") as f:
        files = {"file": f}
        upload_url = f"{DISPATCHER_URL}/upload"
        response = requests.post(upload_url, files=files)

    # If the request was successful, print the response
    if response.status_code == 200:
        print(f"File uploaded successfully: {response.json()}")
        return response.json()[0]
    else:
        print(f"File upload failed with status code: {response.status_code}")


def upload_file_purl(file_path):
    """
    This function uploads a file to Orchestrator and returns the file S3 json.
    """

    # Ensure the file exists
    try:
        with open(file_path, "rb") as f:
            pass
    except FileNotFoundError:
        print(f"No file found at path: {file_path}")
        return

    # Open the file in binary mode and upload it
    with open(file_path, "rb") as f:
        files = {"file": f}
        upload_url = f"{DISPATCHER_URL}/upload_purl"
        response = requests.post(upload_url, files=files)

    # If the request was successful, print the response
    if response.status_code == 200:
        print(f"File uploaded successfully: {response.json()}")
        return response.json()[0]
    else:
        print(f"File upload failed with status code: {response.status_code}")


def map(lst, fn, batch_size=10):
    """Convenience function to maps a function over a list of inputs.

    Args:
        lst (List): The nested list of inputs.
        fn (Callable): The function to map over the list.
        batch_size (Optional[int]): The number of inputs to process in parallel. Defaults to 10. If set to None, will batch all inputs into a single batch.
    """

    fn(_RESERVED_INPUT_KEY)

    if batch_size is None:
        batch_size = len(lst)

    lst = [
        [x] if not hasattr(x, "__iter__") or isinstance(x, str) else (x if isinstance(x, list) else list(x))
        for x in lst
    ]

    batches = [lst[i : i + batch_size] for i in range(0, len(lst), batch_size)]

    results = []
    for batch in batches:
        batch_result = fn([_RESERVED_BATCH_KEY, batch])
        results.extend(batch_result[0][1])

    return results


__all__ = ["register", "run", "handler", "upload_file", "upload_file_purl", "download_from_signed_url", "download_from_file_record", "download_from_registered_file", "map", "set_vars", "DISPATCHER_URL", "TOKEN"]
