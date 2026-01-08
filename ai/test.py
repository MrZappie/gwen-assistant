import os
from utils.stream_print import print_stream
from agent.graph_builder import app


inputs = {"messages": [("user", input("Enter Message: \n"))]}
print_stream(app.stream(inputs, stream_mode="values"))
