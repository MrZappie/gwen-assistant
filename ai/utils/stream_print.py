

from langchain_core.messages import AIMessage, HumanMessage

def print_stream_refined(state, printed_ids):
    """Prints only new messages using the provided set for deduplication."""
    if "messages" not in state:
        return

    for message in state["messages"]:
        if message.id in printed_ids:
            continue
        
        # Only print Human and AI messages
        if isinstance(message, (HumanMessage, AIMessage)):
            if isinstance(message, AIMessage) and message.tool_calls:
                print(f"\n[System]: Calling tools: {[tc['name'] for tc in message.tool_calls]}...")
            
            if message.content.strip():
                print("\n" + "="*20)
                message.pretty_print()
                print("="*20)
            
            printed_ids.add(message.id)