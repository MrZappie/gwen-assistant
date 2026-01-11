



from dotenv import load_dotenv
import os

# Load .env from your project root
load_dotenv(".env",override=True)  # make sure the path is correct


from ai.utils.stream_print import print_stream
from ai.agent.graph_builder import app



inputs = {"messages": [("user", input("Enter Message: \n"))]}
print_stream(app.stream(inputs, stream_mode="values"))