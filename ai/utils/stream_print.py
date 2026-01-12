
from langchain_core.messages import AIMessage, HumanMessage
# 2. Tracking for deduplication
printed_message_ids = set()


def print_stream_refined(state):
    """Prints only new AI/Human messages and avoids duplicates."""
    if "messages" not in state:
        return

    for message in state["messages"]:
        if message.id in printed_message_ids:
            continue
        
        # Only print Human and AI messages
        if isinstance(message, (HumanMessage, AIMessage)):
            # If it's an AI message with tool calls, show a status update
            if isinstance(message, AIMessage) and message.tool_calls:
                print(f"\n[System]: Calling tools: {[tc['name'] for tc in message.tool_calls]}...")
            
            # Print actual content if it exists
            if message.content.strip():
                print("\n" + "="*20)
                message.pretty_print()
                print("="*20)
            
            printed_message_ids.add(message.id)