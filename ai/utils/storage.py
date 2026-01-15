import os
import json
import uuid
import ctypes
import platform
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from config.preferences import get_value # Assuming this exists from your previous code

PROJECT_DIR = get_value("PROJECT_DIR")
# For testing purposes, I'll hardcode or use relative if config is missing
AI_DIR = os.path.join(PROJECT_DIR, ".ai") 
CHAT_DIR = os.path.join(AI_DIR, "chat")

def init_ai_storage():
    """Ensures .ai/chat directories exist."""
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR, exist_ok=True)

        
def serialize_message(m, clean_view=False):
    """
    Converts a message to JSON. 
    If clean_view is True:
    - AI messages with tool calls are ignored (or simplified).
    - Tool messages are simplified to just their output.
    """
    msg_data = {"type": m.type, "content": m.content}
    if hasattr(m, "id") and m.id:
        msg_data["id"] = m.id

    # LOGIC FOR NORMAL (CLEAN) LOG
    if clean_view:
        if isinstance(m, AIMessage):
            # If AI is just calling tools, we might not want it in the clean log 
            # until it gives a final answer. 
            if len(m.tool_calls) != 0:
                return None # Signal to skip this message
        
        if isinstance(m, ToolMessage):
            # Transform Tool result into a simpler "Observation"
            msg_data["tool_call_id"] = m.tool_call_id
            msg_data["content"] = f"Tool Result: {m.content[:200]}..." # Truncated for readability
            msg_data["tool_name"] = getattr(m, "name", "unknown_tool")

    # LOGIC FOR DEBUG (FULL) LOG
    else:
        if isinstance(m, AIMessage) and hasattr(m, "tool_calls"):
            msg_data["tool_calls"] = m.tool_calls
        if isinstance(m, ToolMessage):
            msg_data["tool_call_id"] = m.tool_call_id
            
    return msg_data

def append_to_chat(session_id: str, message, debug=False):
    dir_path = os.path.join(CHAT_DIR, session_id)
    os.makedirs(dir_path, exist_ok=True)
    
    file_path = os.path.join(dir_path, "debug_log.json" if debug else "log.json")

    # If it's the normal log, we want the "clean_view"
    msg_data = serialize_message(message, clean_view=not debug)
    
    # If the filter returned None, don't append anything
    if msg_data is None:
        return

    # Initialize file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("[]")

    with open(file_path, "r+") as f:
        # Move pointer to the end of the file
        f.seek(0, os.SEEK_END)
        pos = f.tell() - 1
        
        # Search backwards for the closing ']'
        while pos > 0:
            f.seek(pos)
            char = f.read(1)
            if char == ']':
                break
            pos -= 1
        
        # If we found the bracket, truncate from there
        if pos > 0:
            f.seek(pos)
            # Check if list is empty "[]" or has items "[...]"
            # We determine this by peeking at the char before the ']'
            f.seek(pos - 1)
            prev_char = f.read(1)
            
            f.seek(pos) # Go back to overwrite ']'
            
            # If the previous char wasn't '[', we need a comma
            if prev_char != '[':
                f.write(",\n")
            
            # Dump the new message and close the list
            json.dump(msg_data, f, indent=2)
            f.write("]")
        else:
            # Fallback if file structure is corrupt
            print("Error: Could not find closing bracket in JSON. Re-saving full chat.")
            # In a real app, you might trigger a full re-save here
            
def load_chat(session_id: str , debug = False):
    """Loads messages from a JSON file."""
    
    dir_path =  os.path.join(CHAT_DIR,session_id)
    
    if debug:
        file_path = os.path.join(dir_path, f"debug_log.json")
    else:
        file_path = os.path.join(dir_path,f"log.json")


    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
        
    messages = []
    for m in data:
        m_type = m.get("type")
        m_content = m.get("content")
        m_id = m.get("id") or str(uuid.uuid4()) # Use saved ID or generate new
        
        if m_type == "human":
            messages.append(HumanMessage(content=m_content, id=m_id))
        elif m_type == "ai":
            messages.append(AIMessage(content=m_content, tool_calls=m.get("tool_calls", []), id=m_id))
        elif m_type == "tool" and not debug:
            messages.append(ToolMessage(content=m_content, tool_call_id=m.get("tool_call_id"), id=m_id , name=m.get("tool_name")))
        elif m_type == "system":
            messages.append(SystemMessage(content=m_content, id=m_id))
            
    return messages