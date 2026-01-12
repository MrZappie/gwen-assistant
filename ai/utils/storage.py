import os
import json
import uuid
import ctypes
import platform
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from config.preferences import get_value

PROJECT_DIR = get_value("PROJECT_DIR")
AI_DIR = os.path.join(PROJECT_DIR, ".ai")
CHAT_DIR = os.path.join(AI_DIR, "chat")

def init_ai_storage():
    """Ensures .ai/chat directories exist and are hidden on Windows."""
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR, exist_ok=True)
        
        if platform.system() == "Windows":
            try:
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ctypes.windll.kernel32.SetFileAttributesW(AI_DIR, FILE_ATTRIBUTE_HIDDEN)
            except Exception as e:
                print(f"Note: Could not set hidden attribute: {e}")
        print(f"Initialized storage at {CHAT_DIR}")

def save_chat(session_id: str, messages: list):
    """Saves messages to a JSON file."""
    file_path = os.path.join(CHAT_DIR, f"{session_id}.json")
    serializable_msgs = []
    
    for m in messages:
        msg_data = {"type": m.type, "content": m.content}
        # Capture tool calls for AI messages
        if isinstance(m, AIMessage) and hasattr(m, "tool_calls"):
            msg_data["tool_calls"] = m.tool_calls
        # Capture tool_call_id for Tool messages
        if isinstance(m, ToolMessage):
            msg_data["tool_call_id"] = m.tool_call_id
        serializable_msgs.append(msg_data)
        
    with open(file_path, "w") as f:
        json.dump(serializable_msgs, f, indent=2)

def load_chat(session_id: str):
    """Loads messages from a JSON file and assigns unique IDs."""
    file_path = os.path.join(CHAT_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r") as f:
        data = json.load(f)
        
    messages = []
    for m in data:
        m_type = m.get("type")
        m_content = m.get("content")
        m_id = str(uuid.uuid4()) # Essential for the duplicate-print checker
        
        if m_type == "human":
            messages.append(HumanMessage(content=m_content, id=m_id))
        elif m_type == "ai":
            messages.append(AIMessage(content=m_content, tool_calls=m.get("tool_calls", []), id=m_id))
        elif m_type == "tool":
            messages.append(ToolMessage(content=m_content, tool_call_id=m.get("tool_call_id"), id=m_id))
        elif m_type == "system":
            messages.append(SystemMessage(content=m_content, id=m_id))
            
    return messages