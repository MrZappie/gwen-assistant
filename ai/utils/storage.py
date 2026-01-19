import os
import json
import uuid
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from config.preferences import get_value 

# --- PATH SETUP ---
# Safety: Default to current working directory if PROJECT_DIR is missing
_proj_dir = get_value("PROJECT_DIR")
PROJECT_DIR = _proj_dir if _proj_dir else os.getcwd()

AI_DIR = os.path.join(PROJECT_DIR, ".ai") 
CHAT_DIR = os.path.join(AI_DIR, "chat")

def init_ai_storage():
    """Ensures .ai/chat directories exist."""
    if not os.path.exists(CHAT_DIR):
        try:
            os.makedirs(CHAT_DIR, exist_ok=True)
        except Exception as e:
            print(f"Error creating chat directory at {CHAT_DIR}: {e}")

def serialize_message(m, clean_view=False):
    """Converts a message to JSON."""
    msg_data = {"type": m.type, "content": m.content}
    if hasattr(m, "id") and m.id:
        msg_data["id"] = m.id

    if clean_view:
        # Hide intermediate AI tool calls from the main chat view
        if isinstance(m, AIMessage):
            if hasattr(m, "tool_calls") and len(m.tool_calls) > 0:
                # Only return if there is actual content alongside the tool call
                if not m.content: 
                    return None 
        
        if isinstance(m, ToolMessage):
            msg_data["tool_call_id"] = m.tool_call_id
            msg_data["content"] = f"Tool Output: {str(m.content)[:100]}..." # Truncate
            msg_data["tool_name"] = getattr(m, "name", "tool")

    else:
        # Debug view gets everything
        if isinstance(m, AIMessage) and hasattr(m, "tool_calls"):
            msg_data["tool_calls"] = m.tool_calls
        if isinstance(m, ToolMessage):
            msg_data["tool_call_id"] = m.tool_call_id
            msg_data["tool_name"] = getattr(m, "name", "tool")
            
    return msg_data

def append_to_chat(session_id: str, message, debug=False):
    """Safely appends a message to the JSON list in the log file."""
    
    # Ensure directory exists for this specific session
    dir_path = os.path.join(CHAT_DIR, session_id)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    file_path = os.path.join(dir_path, "debug_log.json" if debug else "log.json")

    msg_data = serialize_message(message, clean_view=not debug)
    if msg_data is None:
        return

    # --- ROBUST FILE WRITING ---
    # We use a read/modify/write approach for safety on small files, 
    # or the seeking approach if optimization is needed. 
    # The previous seeking approach is good but can be brittle. 
    # Here is a safer, slightly more verbose version of the seeking logic.
    
    try:
        # Initialize if missing
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding='utf-8') as f:
                json.dump([msg_data], f, indent=2)
            return

        # Append to existing
        with open(file_path, "r+", encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            
            # Search backwards for the last closing bracket ']'
            while pos > 0:
                pos -= 1
                f.seek(pos)
                if f.read(1) == "]":
                    break
            
            if pos > 0:
                # We found the closing bracket. Overwrite it.
                f.seek(pos)
                # Check if we need a comma (if list is not just "[]")
                # Peeking back to see if previous char was '['
                f.seek(pos - 1)
                prev_char = f.read(1)
                
                f.seek(pos) # Back to overwrite spot
                
                if prev_char != "[":
                    f.write(",\n")
                
                json.dump(msg_data, f, indent=2)
                f.write("]") # Close the list again
            else:
                # File corrupted or empty? Overwrite.
                f.seek(0)
                json.dump([msg_data], f, indent=2)
                f.truncate()

    except Exception as e:
        print(f"Error appending to chat log: {e}")

def load_chat(session_id: str, debug=False):
    """Loads messages from a JSON file."""
    dir_path = os.path.join(CHAT_DIR, session_id)
    file_path = os.path.join(dir_path, "debug_log.json" if debug else "log.json")

    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
        
    messages = []
    for m in data:
        m_type = m.get("type")
        m_content = m.get("content") or ""
        m_id = m.get("id") or str(uuid.uuid4())
        
        if m_type == "human":
            messages.append(HumanMessage(content=m_content, id=m_id))
        elif m_type == "ai":
            messages.append(AIMessage(content=m_content, tool_calls=m.get("tool_calls", []), id=m_id))
        elif m_type == "tool" and not debug:
             # In clean view, we just show the output as a ToolMessage 
             # (LangChain might expect tool_call_id to match)
            messages.append(ToolMessage(content=m_content, tool_call_id=m.get("tool_call_id", "unknown"), id=m_id, name=m.get("tool_name")))
        elif m_type == "system":
            messages.append(SystemMessage(content=m_content, id=m_id))
            
    return messages

# ai/utils/storage.py

def list_sessions():
    """Returns a list of all session metadata from the filesystem."""
    init_ai_storage()
    sessions = []
    
    if not os.path.exists(CHAT_DIR):
        return []

    # Iterate through every folder in the chat directory
    for session_id in os.listdir(CHAT_DIR):
        dir_path = os.path.join(CHAT_DIR, session_id)
        if not os.path.isdir(dir_path):
            continue
            
        log_path = os.path.join(dir_path, "log.json")
        
        # Default metadata
        session_meta = {
            "id": session_id,
            "lastMessage": "New Conversation",
            "timestamp": os.path.getmtime(dir_path) * 1000 # Convert to JS timestamp
        }

        # Try to get the last message content for the preview
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    if data and len(data) > 0:
                        last_msg = data[-1]
                        session_meta["lastMessage"] = last_msg.get("content", "")[:50]
            except Exception:
                pass
        
        sessions.append(session_meta)

    # Sort sessions by newest first
    sessions.sort(key=lambda x: x["timestamp"], reverse=True)
    return sessions