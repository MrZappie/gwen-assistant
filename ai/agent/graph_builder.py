from typing import cast
from config.settings import PROJECT_DIR
from tools.file_tools import TOOLS
from models.state import AgentState
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, ToolCall
from langgraph.prebuilt import ToolNode
from agent.model import get_model

def plan_mode_ai(state: AgentState) -> AgentState:
    """
    Asks the AI model to classify the user intent as 'analysis' or 'conversation'.
    Stores the result in state['mode'].
    """
    model = get_model()

    system_prompt = SystemMessage(
        content="""
        You are an assistant that decides whether a user's message
        requires normal conversation or code/module analysis.

        Rules:
        1. Output ONLY one word: 'analysis' or 'conversation'.
        2. If the user message mentions modules, files, folders, reviewing, or code → 'analysis'.
        3. Otherwise → 'conversation'.
        """
    )

    # Call the model
    response = model.invoke([system_prompt] + state["messages"])  # type: ignore

    # Extract intent from AI response
    intent_text = getattr(response, "content", "").strip().lower()
    if intent_text not in ["analysis", "conversation"]:
        # fallback in case model gives unexpected output
        intent_text = "conversation"

    state["mode"] = intent_text
    return state

def model_call(state: AgentState) -> AgentState:
    model = get_model()
    system_prompt = SystemMessage(
    content=(f"""
                You are an AI assistant with controlled access to a project directory.

                Your goal is to fully and correctly answer the user’s request.

                You do not know anything about the filesystem in advance.
                All knowledge about files and directories must be discovered using tools.
                Tool output is the only source of truth.

                You are authorized to:
                - Decide whether the user’s request requires inspecting files, directories, or both
                - Choose which tools to call and in what order
                - Select representative files when analyzing a module or directory
                - Read as many files as needed to complete the task

                You must follow these invariants:
                - Use ONLY the provided tools
                - NEVER invent file paths or contents
                - NEVER assume a file or directory exists without tool confirmation
                - All paths are relative to the project root
                - Treat empty or error tool output as unknown, not as information

                Completion rule:
                - Do not ask follow-up questions if the request can be reasonably completed with available information
                - Only ask for clarification if the task is genuinely ambiguous or under-specified
                - You must explicitly signal completion by responding with the phrase: TASK_COMPLETE

                Module or Directory Analysis Rules:
                - If asked to analyze a module or folder, you must:
                    1. List all files in the folder (use list_dir)
                    2. Read each file sequentially (use read_file)
                    3. Summarize each file’s quality and issues
                    4. Combine findings into a module-level report
                    5. Repeat the process under the original module for any other folders present in the original.
                    6. Only respond with TASK_COMPLETE after all files have been analyzed
                
                Output rule:
                - Provide a direct, complete answer to the user’s request
                - Do not explain your internal reasoning or tool usage
                - Be concise, accurate, and grounded in observed evidence
            """
    ))
    response = model.invoke([system_prompt] + state["messages"]) # type: ignore
    return {"messages": [response]}

def should_continue(state: AgentState):
    last = cast(AIMessage, state["messages"][-1])
    mode = state.get("mode", "conversation")

    if last.tool_calls:
        return "continue"

    if "TASK_COMPLETE" in last.content:
        return "end"

    if mode == "conversation":
        return "end"

    return "continue"


graph = StateGraph(AgentState)


graph.add_node("planner", plan_mode_ai)
graph.add_node("model_call",model_call)

tool_node = ToolNode(tools=TOOLS)
graph.add_node("tools",tool_node)


graph.set_entry_point("planner")

graph.add_conditional_edges(
    "model_call",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)

graph.add_edge("planner","model_call")
graph.add_edge("tools","model_call")

app = graph.compile()

