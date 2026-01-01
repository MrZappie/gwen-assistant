from langchain_groq import ChatGroq
from config.settings import API_KEY ,MODE
from tools.file_tools import TOOLS
from langchain_ollama import ChatOllama


groq_model = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        api_key=API_KEY,
    ).bind_tools(TOOLS)

ollama_model = ChatOllama(
    model = "qwen2.5:14b",
    temperature=0
).bind_tools(TOOLS)

def get_model():
    return ollama_model if MODE == "LOCAL" else groq_model