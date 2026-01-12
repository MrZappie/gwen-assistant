import sys
import itertools
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from ai.utils.stream_print import print_stream_refined

load_dotenv(".env", override=True)
# Import internal logic
from ai.agent.graph_builder import app
from ai.utils.storage import init_ai_storage, save_chat, load_chat


# 1. Setup & Session Selection
init_ai_storage()
session_id = 1
past_messages = load_chat(session_id)

# 2. Tracking for deduplication
printed_message_ids = set()
for m in past_messages:
    printed_message_ids.add(m.id)

state = {"messages": past_messages}
spinner = itertools.cycle(['-', '/', '|', '\\'])

# 3. Execution Loop
print(f"--- Session '{session_id}' active ({len(past_messages)} messages loaded) ---")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "q":
        save_chat(session_id, state["messages"])
        print("Session saved. Bye!")
        break

    # Add user message to state
    user_msg = HumanMessage(content=user_input, id=str(uuid.uuid4()))
    state["messages"].append(user_msg)
    # Add to printed set immediately so the stream doesn't print it back to you
    printed_message_ids.add(user_msg.id)

    print("AI is thinking...", end=" ", flush=True)
    
    final_state = state
    for event in app.stream(state, stream_mode="values"):
        # Update Spinner
        sys.stdout.write('\b' + next(spinner))
        sys.stdout.flush()
        
        final_state = event
        print_stream_refined(event)

    state = final_state
    save_chat(session_id, state["messages"])