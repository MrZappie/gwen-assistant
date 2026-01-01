from langchain_groq import ChatGroq
from config.settings import API_KEY
from tools.file_tools import TOOLS

def create_model():
    return ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        api_key=API_KEY,
    ).bind_tools(TOOLS)