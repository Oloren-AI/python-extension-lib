import socketio
import uuid
import json
import requests


def run_blue_node(graph, node_id, dispatcher_url, inputs):
    socket_url = dispatcher_url.replace("http://", "ws://").replace("https://", "wss://")

    socket = socketio.Client()
    maxId = max([outputId["id"] for outputId in graph["output_ids"]]) + 1
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

    graph["id"] = f"{uid}-graph"
    graph["input_ids"] = [el["output_ids"][0] for el in newElements]

    @socket.on("connect")
    def connect():
        print("CONNECTED!")

        def on_extensionregister_response(*args):
            print("Am inside extension register response")
            client_uuid = args[0]
            response = requests.post(
                f"{socket_url}/run_graph",
                data=json.dumps({"graph": newGraph, "uuid": client_uuid}),
                headers={"Content-Type": "application/json"},
            )
            print("Registered with dispatcher")

        socket.emit("extensionregister", data={"id": uid}, callback=on_extensionregister_response)

    @socket.on("node")
    def node(node_data):
        print("RECEIVED NODE!")
        if graph["id"] == node_data.data.id:
            if node_data["status"] == "finished":
                socket.disconnect()
                if len(node_data["data"]["output_ids"]) > 0:
                    return node_data.output
            elif node_data["status"] != "running":
                socket.disconnect()
                raise Exception("Fn failed to run: " + json.dumps(node_data))

    print(socket_url)
    socket.connect(socket_url)
    socket.wait()


if __name__ == "__main__":
    import sys
    import json

    pass
