from typing import cast
from models.state import AgentState
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage, ToolCall
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

PROJECT_DIR = os.getenv("PROJECT_DIR")

def safe_path(user_path: str) -> str:
    """
    Resolve user-provided paths safely inside PROJECT_DIR.
    Raises ValueError if access is outside the sandbox.
    """
    # Join with project root
    joined_path = os.path.join(PROJECT_DIR, user_path)

    # Resolve symlinks, ../, etc.
    resolved_path = os.path.realpath(joined_path)

    # Enforce sandbox
    if not resolved_path.startswith(PROJECT_DIR):
        raise ValueError("Access denied: path outside project directory")

    return resolved_path

@tool
def read_file(path: str) -> str:
    """
    Reads the contents of any file inside the project directory.
    Path must be relative to the project root.
    """
    try:
        safe = safe_path(path)
        with open(safe, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return str(e)

import difflib

@tool
def find_file(filename: str) -> str:
    """
    Search for a file by name inside the project directory.
    Returns relative paths.
    If exact match is not found, returns similar filenames with their relative paths.
    """
    import difflib

    matches = []
    all_files = []

    for root, _, files in os.walk(PROJECT_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, PROJECT_DIR).replace("\\", "/")
            all_files.append((f, rel_path))
            if f == filename:
                matches.append(rel_path)

    if matches:
        return "Exact matches:\n" + "\n".join(matches)

    # fuzzy suggestions with paths
    filenames_only = [f for f, _ in all_files]
    suggestions = difflib.get_close_matches(filename, filenames_only, n=5, cutoff=0.6)

    if suggestions:
        suggestion_paths = [rel for f, rel in all_files if f in suggestions]
        return (
            "No exact match found.\n"
            "Similar files with paths:\n" +
            "\n".join(suggestion_paths)
        )

    return "No matching or similar files found."


@tool
def list_dir(path: str) -> str:
    """
    List files and folders directly inside a directory (non-recursive).
    Path must be relative to the project root.
    """
    try:
        safe = safe_path(path)

        if not os.path.isdir(safe):
            return f"Not a directory: {path}"

        entries = []
        for name in os.listdir(safe):
            full_path = os.path.join(safe, name)
            rel_path = os.path.relpath(full_path, PROJECT_DIR)
            rel_path = rel_path.replace("\\", "/")

            if os.path.isdir(full_path):
                entries.append(f"[DIR] {rel_path}")
            else:
                entries.append(f"[FILE] {rel_path}")

        return "\n".join(sorted(entries))
    except Exception as e:
        return str(e)


@tool
def write_tool(text: str, file_path: str):
    """
    Writes text to a file inside the project directory.
    Overwrites if it exists.
    """
    try:
        safe = safe_path(file_path)
        os.makedirs(os.path.dirname(safe), exist_ok=True)
        with open(safe, "w", encoding="utf-8") as f:
            f.write(text)
        return "File Written Successful"
    except Exception as e:
        return str(e)



tools = [write_tool,list_dir,read_file,find_file]

model = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        api_key=API_KEY,
    ).bind_tools(tools)



def model_call(state: AgentState) -> AgentState:
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

tool_node = ToolNode(tools=tools)
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

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", input("Enter Message: \n"))]}
print_stream(app.stream(inputs,stream_mode="values"))
