import os
from dotenv import load_dotenv

API_KEY = os.getenv("GROQ_API_KEY")
MODE = os.getenv("MODE", "dev")

PROJECT_DIR = os.getenv("PROJECT_DIR")
if not PROJECT_DIR:
    raise RuntimeError(
        "PROJECT_DIR is not set. Add it to your .env file "
        "(e.g., PROJECT_DIR=D:/GWEN)"
    )

PROJECT_DIR = os.path.realpath(PROJECT_DIR)
