from .server import *

from typing import Any
import requests
import uuid
import json

class API:

    def __init__(self, appDb, sessionId):
        self.appDb = appDb
        self.sessionId = sessionId
        
    def __repr__(self):
        return self.appDb["name"] + ": " + f"inputs = {self.appDb['inputs']}; outputs = {self.appDb['outputs']}; description = {self.appDb.get('description', )}"
    
    def __call__(self, *args, **kwargs):
        
        assert len(args) == len(self.appDb["inputs"]), f"Expected {len(self.appDb['inputs'])} inputs, got {len(args)}."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['TOKEN']}" if config['TOKEN'] else None
        }
        
        data = {
            "uuid": self.sessionId,
            **{
                self.appDb["inputs"][i]: args[i] for i in range(len(args))
            }
        }
        
        url = config["DISPATCHER_URL"] + "/api/run/" + self.appDb["name"]

        print("Launching app in session ", self.sessionId)
        res = requests.post(url, headers=headers, json=data)

        if res.status_code != 200:
            print(res.text)
            print(f"Failed to launch API call: {self.appDb['url']}. Please check your password.")
            return None
        else:
            outputs = res.json()
            assert len(outputs.keys()) == len(self.appDb["outputs"]), f"Expected {len(self.appDb['outputs'])} outputs, got {len(outputs.keys())}."
            
            return (*[outputs[key] for key in self.appDb["outputs"]],)
            
        

API_EXPOSED_ATTRIBUTES = ["__init__", "begin", "apisList", "ALL_APIS", "ALL_APIS_BASIC_INFO", "API_INFO", "sessionId"]

class Client_:
    def __init__(self):
        self.apisList = None
    
    def begin(self, sessionId = None):
        assert config["DISPATCHER_URL"] is not None, "Dispatcher URL not set, set with olo.config['DISPATCHER_URL'] = '...'"
        assert config["TOKEN"] is not None, "Token not set, set with olo.config['TOKEN'] = '...'"
        
        self.apisList = requests.get(f"{config['DISPATCHER_URL']}/apps",
            headers={
                "Authorization": f"Bearer {config['TOKEN']}"
            }
        ).json()
        if not sessionId:
            self.sessionId = str(uuid.uuid4())
        else:
            self.sessionId = sessionId
            
        print("Beginning session ", self.sessionId)
        
    def ALL_APIS(self):
        return [x["name"] for x in self.apisList if len(x["outputs"]) > 0]
    
    def ALL_APIS_BASIC_INFO(self):
        return [{"name": x["name"],
                 "inputs": x["inputs"],
                 "outputs": x["outputs"],}
                 for x in self.apisList if len(x["outputs"]) > 0]
    
    def API_INFO(self, app_name):
        return [x for x in self.apisList if x["name"] == app_name][0]
        
    def __getattribute__(self, __name: str) -> Any:
        if __name in API_EXPOSED_ATTRIBUTES:
            return object.__getattribute__(self, __name)

        if self.apisList and self.ALL_APIS() and __name in self.ALL_APIS():
            return API([x for x in self.apisList if x["name"] == __name][0], self.sessionId)

Client = Client_()
