import json
import os
import uuid
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
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/chat/{session_id}")
async def chat_endpoint(session_id: str, payload: ChatRequest):
    user_input = payload.message

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
        yield json.dumps({
            "type": "human",
            "content": user_input,
        }) + "\n"

        for event in app.stream(state, stream_mode="values"):
            if "messages" not in event:
                continue

            for msg in event["messages"]:
                if not hasattr(msg, "id") or msg.id in processed_ids:
                    continue

                append_to_chat(session_id, msg, debug=False)
                append_to_chat(session_id, msg, debug=True)

                if isinstance(msg, (HumanMessage, AIMessage)):
                    msg_data = serialize_message(msg)
                    if msg_data:
                        yield json.dumps(msg_data) + "\n"

                processed_ids.add(msg.id)

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
    )