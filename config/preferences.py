

import json
from pathlib import Path


def preference_init():
    data_path = Path("data.json")
    if not data_path.exists():
        with data_path.open("w") as f:
            json.dump({
                "PROJECT_DIR": "",
                "MODE": "LOCAL"
            }, f,indent=4)
        
        print("[DATA-INIT]:DATA json file created with default value")
        return
    print("[DATA-INIT]: DATA json initialized")

def set_value(key: str , value):
    with open("data.json", "r") as file:
        data = json.load(file)

    data[key] = value

    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

def get_value(key: str) -> str:
    data = None
    with open("data.json", "r") as file:
        data = json.load(file)

    if key in data:
        return data[key]
    return ValueError("[KEY-ERROR]:No such key exists in data.json file")