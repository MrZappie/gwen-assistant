

import json
from pathlib import Path


def preference_init():
    data_path = Path("data.json")
    if not data_path.exists():
        with data_path.open("w") as f:
            json.dump({
                "PROJECT_DIR": "",
                "MODE": "LOCAL"
            }, f)
        
        print("[DATA-INIT]:DATA json file created with default value")
        return
    print("[DATA-INIT]: DATA json initialized")

