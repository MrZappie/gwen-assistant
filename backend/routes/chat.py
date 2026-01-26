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
    CHAT_DIR,
    serialize_message,
)

load_dotenv(override=True)

router = APIRouter()
init_ai_storage()

# -------------------------------------------------
# GET CHAT HISTORY
# -------------------------------------------------
@router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """
    Returns the clean (non-debug) chat log.
    """
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

    past_messages = load_chat(session_id, debug=False)
    processed_ids = {m.id for m in past_messages if hasattr(m, "id")}

    user_msg = HumanMessage(
        content=user_input,
        id=str(uuid.uuid4())
    )

    if user_msg.id not in processed_ids:
        append_to_chat(session_id, user_msg, debug=False)
        append_to_chat(session_id, user_msg, debug=True)
        processed_ids.add(user_msg.id)

    state = {
        "chat_history": past_messages,
        "messages": [user_msg],
    }

    async def event_generator():
        # Echo user message first
        yield json.dumps({
            "type": "human",
            "content": user_input,
        }) + "\n"

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
    session_dir = os.path.join(CHAT_DIR, session_id)

    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        shutil.rmtree(session_dir)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
