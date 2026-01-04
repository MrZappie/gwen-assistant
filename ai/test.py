import os
from pathlib import Path
from utils.stream_print import print_stream
from agent.graph_builder import app

env_path = Path(".env")
required_keys = ["GROQ_API_KEY", "PROJECT_DIR", "MODE"]

# -------------------------------
if not env_path.exists():
    # Create .env with placeholders
    with env_path.open("w") as f:
        f.write("GROQ_API_KEY=\n")
        f.write(f"PROJECT_DIR={os.getcwd()}\n")
        f.write("MODE=LOCAL\n")
    print(
        "Created .env file with placeholders.\n"
        "Please fill in GROQ_API_KEY if you want to use ONLINE mode.\n"
        "PROJECT_DIR is set to current directory by default.\n"
        "Run the script again after filling the .env file."
    )
    exit(0)

from dotenv import dotenv_values

env_values = dotenv_values(env_path)

missing_keys = [k for k in required_keys if k not in env_values or not env_values[k].strip()]
if missing_keys:
    print(f"The following keys are missing or empty in your .env file: {', '.join(missing_keys)}")
    print("Please fill them before running the script.")
    exit(0)

inputs = {"messages": [("user", input("Enter Message: \n"))]}
print_stream(app.stream(inputs, stream_mode="values"))
