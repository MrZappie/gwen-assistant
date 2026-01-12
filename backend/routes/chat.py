import json
import os
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from ai.agent.graph_builder import app as agent_app
from ai.utils.storage import (
    init_ai_storage, 
    append_to_chat, 
    load_chat, 
    CHAT_DIR,
    serialize_message
)

router = APIRouter()


@router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """
    Endpoint 1: Load chat history.
    Reads the raw JSON file directly to be fast.
    """
    file_path = os.path.join(CHAT_DIR, f"{session_id}.json")
    if not os.path.exists(file_path):
        return [] # Return empty list if no session exists
    
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/{session_id}")
async def chat_endpoint(session_id: str, user_input: str):
    """
    Endpoint 2: Give user input to model.
    Streams the response back event-by-event.
    """
    
    # 1. Re-hydrate State (Load history from disk)
    # Since HTTP is stateless, we must reload context every time.
    past_messages = load_chat(session_id)
    
    # Create the set of IDs we already know about to avoid duplicates
    saved_message_ids = {m.id for m in past_messages}
    
    # 2. Add User Message
    user_msg_id = str(uuid.uuid4())
    user_msg = HumanMessage(content=user_input, id=user_msg_id)
    
    # Append to storage immediately
    append_to_chat(session_id, user_msg)
    saved_message_ids.add(user_msg_id)
    
    # Add to in-memory state for the graph
    past_messages.append(user_msg)
    state = {"messages": past_messages}

    # 3. Generator Function (The Logic Stream)
    async def event_generator():
        # Yield the user message first so frontend sees it was accepted
        yield json.dumps({"type": "human", "content": user_input.content}) + "\n"

        # Stream the graph execution
        current_state = state
        for event in agent_app.stream(current_state, stream_mode="values"):
            
            if "messages" in event:
                for msg in event["messages"]:
                    # We only care about NEW messages we haven't processed yet
                    if hasattr(msg, "id") and msg.id and msg.id not in saved_message_ids:
                        
                        # A. Save to Disk (Backend Persistence)
                        append_to_chat(session_id, msg)
                        saved_message_ids.add(msg.id)
                        
                        # B. Serialize for Frontend
                        # We use your helper to turn the object into a dict
                        msg_data = serialize_message(msg)
                        
                        # Yield line-delimited JSON
                        yield json.dumps(msg_data) + "\n"
                        
            # Update state for next iteration
            current_state = event

    # Return a Streaming Response
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")