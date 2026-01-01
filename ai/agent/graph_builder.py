from typing import cast
from config.settings import PROJECT_DIR
from tools.file_tools import TOOLS
from models.state import AgentState
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, ToolCall
from langgraph.prebuilt import ToolNode
from agent.model import create_model


def model_call(state: AgentState) -> AgentState:
    model = create_model()
    system_prompt = SystemMessage(
    content=(f"""
                You are an AI assistant with controlled access to a project directory.
                Answer questions about the files and folders using ONLY the provided tools.

                You do NOT know file paths in advance.
                You must discover all filesystem information via tools.

                Root directory (PROJECT_DIR): {PROJECT_DIR}

                STRICT RULES:
                - You may ONLY use the tools that are explicitly provided
                - NEVER attempt web search or external tools
                - All paths are RELATIVE to PROJECT_DIR
                - Use forward slashes (/) for all paths
                - NEVER invent paths or filenames
                - NEVER assume a file or folder exists

                FILE DISCOVERY RULES:
                - To locate a file by name, use the find_file tool
                - Only use list_dir to inspect the contents of a known directory
                - list_dir is NON-recursive; it shows only immediate contents
                - Do NOT guess directory structures

                FILE READING RULES:
                - Only read a file after its exact relative path has been confirmed by tools
                - NEVER read a file unless its existence is verified
                - If multiple matching files exist, ask the user which one to use or summarize all

                GENERAL RULES:
                - If a user request is ambiguous (file vs folder vs concept), ask for clarification BEFORE calling tools
                - Do NOT explain your reasoning or exploration steps
                - Treat tool outputs as the ONLY source of truth
                - Reply in clear, concise English
                - You must differentiate between file and folder

            """
    ))
    response = model.invoke([system_prompt] + state["messages"]) # type: ignore
    return {"messages": [response]}

def should_continue(state: AgentState):

    message = state["messages"]
    last_message = cast(AIMessage,message[-1])
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


graph = StateGraph(AgentState)

graph.add_node("model_call",model_call)

tool_node = ToolNode(tools=TOOLS)
graph.add_node("tools",tool_node)

graph.set_entry_point("model_call")

graph.add_conditional_edges(
    "model_call",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)

graph.add_edge("tools","model_call")

app = graph.compile()

