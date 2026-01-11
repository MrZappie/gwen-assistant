def print_stream(state):
    if "messages" not in state:
        return

    message = state["messages"][-1]

    if hasattr(message, "pretty_print"):
        message.pretty_print()
    else:
        print(message)
