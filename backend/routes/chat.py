import json
import os
import shutil
import uuid
import asyncio
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage, AIMessage

from ai.agent.graph_builder import app
from ai.models.chat_request import ChatRequest
from ai.utils.storage import (
    init_ai_storage,
    append_to_chat,
    load_chat,
    serialize_message,
)
from config.preferences import get_value

load_dotenv(override=True)

router = APIRouter()
init_ai_storage()

def load_conversation_context(session_id: str, limit: int = 6):
    """
    Load only the last N human/AI messages for conversational continuity.
    """
    messages = load_chat(session_id, debug=False)
    context = []

    for m in reversed(messages):
        if isinstance(m, (HumanMessage, AIMessage)):
            context.append(m)
        if len(context) >= limit:
            break

    return list(reversed(context))


# -------------------------------------------------
# GET CHAT HISTORY
# -------------------------------------------------
@router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """
    Returns the clean (non-debug) chat log.
    """
    
    PROJECT_DIR = get_value("PROJECT_DIR")

    AI_DIR = os.path.join(PROJECT_DIR, ".ai") 
    CHAT_DIR = os.path.join(AI_DIR, "chat")
    dir_path = os.path.join(CHAT_DIR, session_id)
    file_path = os.path.join(dir_path, "log.json")

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# CHAT STREAM ENDPOINT
# -------------------------------------------------
@router.post("/chat/{session_id}")
async def chat_endpoint(session_id: str, payload: ChatRequest):
    user_input = payload.message
    print("POST /api/chat HIT:", session_id, user_input)

    # --- Load persisted chat (UI only) ---
    past_messages = load_chat(session_id, debug=False)
    processed_ids = {m.id for m in past_messages if hasattr(m, "id")}

    # --- Create user message ---
    user_msg = HumanMessage(
        content=user_input,
        id=str(uuid.uuid4())
    )

    # --- Persist user message immediately ---
    if user_msg.id not in processed_ids:
        append_to_chat(session_id, user_msg, debug=False)
        append_to_chat(session_id, user_msg, debug=True)
        processed_ids.add(user_msg.id)

    # --- Build SHORT agent context ---
    conversation_context = load_conversation_context(session_id, limit=6)

    # --- Initialize agent state (NEW ARCHITECTURE) ---
    state = {
        "user_input": user_input,
        "messages": conversation_context,
        "plan": [],
        "current_step": 0,
        "observations": [],
        "done": False,
    }

    async def event_generator():
        loop = asyncio.get_running_loop()

        def run_graph():
            return list(app.stream(state, stream_mode="values"))

        try:
            events = await loop.run_in_executor(None, run_graph)

            for event in events:
                if "messages" not in event:
                    continue

                for msg in event["messages"]:
                    if not hasattr(msg, "id") or msg.id in processed_ids:
                        continue

                    # Persist AI output
                    append_to_chat(session_id, msg, debug=False)
                    append_to_chat(session_id, msg, debug=True)

                    msg_data = serialize_message(msg)
                    if msg_data:
                        yield json.dumps(msg_data) + "\n"

                    processed_ids.add(msg.id)

        except Exception as e:
            print("STREAM ERROR:", e)
            yield json.dumps({
                "type": "system",
                "content": "Internal error during AI processing."
            }) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"
    )


# -------------------------------------------------
# LIST ALL SESSIONS
# -------------------------------------------------
@router.get("/sessions")
async def get_all_sessions():
    """
    Returns a list of all available chat sessions on the server.
    """
    try:
        from ai.utils.storage import list_sessions
        return list_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    import shutil

@router.delete("/chat/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Deletes a chat session and its stored history.
    """
    
    PROJECT_DIR = get_value("PROJECT_DIR")

    AI_DIR = os.path.join(PROJECT_DIR, ".ai") 
    CHAT_DIR = os.path.join(AI_DIR, "chat")
    session_dir = os.path.join(CHAT_DIR, session_id)

    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        shutil.rmtree(session_dir)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

