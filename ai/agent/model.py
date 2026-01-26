from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from ai.tools.tool_registry import TOOLS
from config.preferences import get_value
import os


def get_model(bind: bool = False):
    MODE = get_value("MODE")

    if MODE == "LOCAL":
        model = ChatOllama(
            model="qwen2.5:14b",
            temperature=0,
        )
    else:
        model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    return model.bind_tools(TOOLS) if bind else model
