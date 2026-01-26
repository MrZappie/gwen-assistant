import sys
import itertools
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from ai.utils.stream_print import print_stream_refined
from ai.agent.graph_builder import app
from ai.utils.storage import init_ai_storage, append_to_chat, load_chat

load_dotenv(".env", override=True)
# 1. Setup
init_ai_storage()
session_id = "session_1"
# Always load from the normal log (debug=False)
past_messages = load_chat(session_id, debug=False)

# 2. Single Tracking Set
processed_ids = {m.id for m in past_messages if hasattr(m, "id")}

state = {"chat_history": past_messages , "messages": []}
print(f"--- Session '{session_id}' active ---")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "q": break

    user_msg = HumanMessage(content=user_input, id=str(uuid.uuid4()))
    state["messages"].append(user_msg)
    
    # Process User Message immediately
    if user_msg.id not in processed_ids:
        append_to_chat(session_id, user_msg, debug=False) # Normal log
        append_to_chat(session_id, user_msg, debug=True)  # Debug log
        processed_ids.add(user_msg.id)

    final_state = state
    for event in app.stream(state, stream_mode="values"):
        final_state = event
        
        if "messages" in event:
            for msg in event["messages"]:
                if msg.id not in processed_ids:
                    # A. LOGGING (Save everything: AI, Tool, System)
                    append_to_chat(session_id, msg, debug=False)
                    append_to_chat(session_id, msg, debug=True)
                    
                    # B. UI DISPLAY (Filter for AI and Human only)
                    if isinstance(msg, (HumanMessage, AIMessage)):
                        # Pass a dummy set or logic to print_stream_refined 
                        # so it only sees this specific new message
                        print_stream_refined(event, processed_ids)
                    
                    # C. MARK AS PROCESSED
                    processed_ids.add(msg.id)

    state = final_state