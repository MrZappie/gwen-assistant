from langchain_groq import ChatGroq
from ai.tools.file_tools import TOOLS
from langchain_ollama import ChatOllama
from config.preferences import get_value
import os

groq_model = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        api_key=os.environ.get("GROQ_API_KEY"),
    ).bind_tools(TOOLS)

ollama_model = ChatOllama(
    model = "qwen2.5:14b",
    temperature=0
).bind_tools(TOOLS)

def get_model():
    MODE = get_value("MODE")
    return ollama_model if MODE == "LOCAL" else groq_model