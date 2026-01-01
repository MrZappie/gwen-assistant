
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

PROJECT_DIR =  os.path.realpath(os.getenv("PROJECT_DIR"))
