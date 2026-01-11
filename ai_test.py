#this was edited
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from ai.utils.stream_print import print_stream
from ai.agent.graph_builder import app
from langchain_core.messages import HumanMessage

# Initialize persistent state
state = {"messages": []}

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "q":
        break

    from langchain_core.messages import HumanMessage
    state["messages"].append(HumanMessage(content=user_input))

    final_state = None
    for event in app.stream(state, stream_mode="values"):
        final_state = event
        print_stream(event)

    state = final_state
