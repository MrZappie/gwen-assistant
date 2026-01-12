import sys
import itertools
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from ai.utils.stream_print import print_stream_refined
from ai.agent.graph_builder import app
from ai.utils.storage import init_ai_storage, append_to_chat, load_chat

load_dotenv(".env", override=True)

# 1. Setup & Session Selection
init_ai_storage()
session_id = 1
past_messages = load_chat(session_id)

# 2. Tracking for deduplication
printed_message_ids = set()
saved_message_ids = set() # NEW: Track what is already on disk

for m in past_messages:
    printed_message_ids.add(m.id)
    saved_message_ids.add(m.id)

state = {"messages": past_messages}
spinner = itertools.cycle(['-', '/', '|', '\\'])

print(f"--- Session '{session_id}' active ({len(past_messages)} messages loaded) ---")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "q":
        break

    # Add user message
    user_msg = HumanMessage(content=user_input, id=str(uuid.uuid4()))
    state["messages"].append(user_msg)
    printed_message_ids.add(user_msg.id)
    
    # SAVE POINT 1: Append User Message
    if user_msg.id not in saved_message_ids:
        append_to_chat(session_id, user_msg)
        saved_message_ids.add(user_msg.id)

    print("AI is thinking...", end=" ", flush=True)
    
    final_state = state
    for event in app.stream(state, stream_mode="values"):
        sys.stdout.write('\b' + next(spinner))
        sys.stdout.flush()
        
        final_state = event
        print_stream_refined(event,printed_message_ids)

        # SAVE POINT 2: Append New AI/Tool Messages
        if "messages" in event:
            # Iterate through the returned messages (LangGraph often returns the full list or chunks)
            # We filter for ones we haven't saved yet.
            for msg in event["messages"]:
                if hasattr(msg, "id") and msg.id and msg.id not in saved_message_ids:
                    append_to_chat(session_id, msg)
                    saved_message_ids.add(msg.id)

    state = final_state