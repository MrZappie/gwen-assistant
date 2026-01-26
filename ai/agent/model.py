from langchain_groq import ChatGroq
from ai.tools.tool_registry import TOOLS
from langchain_ollama import ChatOllama
from config.preferences import get_value
import os

def get_model(bind = False):
    MODE = get_value("MODE")
    if MODE == "LOCAL":
        model =  ChatOllama(
            model = "qwen2.5:14b",
            temperature=0
        )
    else:
        model = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            api_key=os.environ.get("GROQ_API_KEY"),
        )
    
    if bind:
        return model.bind_tools(TOOLS)
    else:
        return model