import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from ai.agent.graph_builder import app
from ai.utils.storage import init_ai_storage, append_to_chat, load_chat
from ai.utils.stream_print import print_stream_refined

load_dotenv(".env", override=True)

# -------------------------------------------------
# Helpers
# -------------------------------------------------

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
# Setup
# -------------------------------------------------

init_ai_storage()
session_id = "session_1"

print(f"--- Session '{session_id}' active ---")

# Track already-logged messages
past_messages = load_chat(session_id, debug=False)
processed_ids = {m.id for m in past_messages if hasattr(m, "id")}

# -------------------------------------------------
# Main Loop
# -------------------------------------------------

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "q":
        break

    # --- Create & persist user message ---
    user_msg = HumanMessage(
        content=user_input,
        id=str(uuid.uuid4())
    )

    if user_msg.id not in processed_ids:
        append_to_chat(session_id, user_msg, debug=False)
        append_to_chat(session_id, user_msg, debug=True)
        processed_ids.add(user_msg.id)

    # --- Build short conversational context ---
    conversation_context = load_conversation_context(session_id, limit=6)

    # --- Initialize NEW agent state ---
    state = {
        "user_input": user_input,
        "messages": conversation_context,
        "plan": [],
        "current_step": 0,
        "observations": [],
        "done": False,
    }

    # --- Run graph ---
    final_state = state

    for event in app.stream(state, stream_mode="values"):
        final_state = event

        if "messages" not in event:
            continue

        for msg in event["messages"]:
            if not hasattr(msg, "id") or msg.id in processed_ids:
                continue

            # A. Persist everything
            append_to_chat(session_id, msg, debug=False)
            append_to_chat(session_id, msg, debug=True)

            # B. Display only conversational output
            if isinstance(msg, AIMessage):
                print_stream_refined(event, processed_ids)

            processed_ids.add(msg.id)
