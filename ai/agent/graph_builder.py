from typing import cast
from ai.tools.tool_registry import TOOLS
from ai.models.state import AgentState
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage , HumanMessage
from langgraph.prebuilt.tool_node import ToolNode

from ai.agent.model import get_model

MAX_MESSAGE = 15

def plan_mode_ai(state: AgentState) -> AgentState:
    model = get_model()

    system_prompt = SystemMessage(
        content="""
        You are an assistant that decides whether a user's message
        requires normal conversation or code/module analysis for the next coder assistant.

        Rules:
        1. Output ONLY one word: 'analysis' or 'conversation'.
        2. If the user message mentions modules, files, folders, reviewing, or code → 'analysis'.
        3. Otherwise → 'conversation'.
        """
    )

    # ONLY last user message
    last_user = next(
        m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)
    )

    response = model.invoke([system_prompt, last_user])

    intent = response.content.strip().lower()
    if intent not in ("analysis", "conversation"):
        intent = "conversation"

    return {"mode": intent}


def model_call(state: AgentState) -> AgentState:
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
                                        - When tasked with query that needs to be used with multiple directories and files, use tools that takes and gives out result for multple directories or files.

                                        Completion rule:
                                        - Do not ask follow-up questions if the request can be reasonably completed with available information
                                        - Only ask for clarification if the task is genuinely ambiguous or under-specified
                                        - You must explicitly signal completion by responding with the phrase: TASK_COMPLETE

                                        Module or Directory Analysis Rules:
                                        - If asked to analyze a module or folder, you must:
                                            1. Call list_dir_recursive ONLY ONCE to understand structure.
                                            2. Then decide which files are important.
                                            3. Read files using read_multiple_files.
                                            4. Summarize each file’s quality and issues
                                            5. Combine findings into a module-level report
                                            6. Repeat the process under the original module for any other folders present in the original.
                                            7. Only respond with TASK_COMPLETE after all files have been analyzed
                                        
                                        Output rule:
                                        - Provide a direct, complete answer to the user’s request
                                        - Do not explain your internal reasoning or tool usage
                                        - Be concise, accurate, and grounded in observed evidence
                                    """
                        ))
    model = get_model(bind=True)    
    
    def messages_for_model(messages):
        return [
            m for m in messages
            if not isinstance(m, ToolMessage)
        ]


    response = model.invoke([system_prompt] +  messages_for_model(state["chat_history"][-10:]) + state["messages"][:]) # type: ignore
    return {"messages": [response]}

def should_continue(state: AgentState):
    last = cast(AIMessage, state["messages"][-1])
    mode = state.get("mode", "conversation")

    if last.tool_calls:
        return "continue"

    if "TASK_COMPLETE" in last.content.strip():
        return "end"

    if mode == "conversation":
        return "end"

    return "reflect"

def reflect(state: AgentState) -> AgentState:
    return {
            "messages": [
                SystemMessage(
                    content=(
                        "You did not call a tool and did not say TASK_COMPLETE. "
                        "If you are done, respond with ONLY: TASK_COMPLETE. "
                        "Otherwise, proceed with the next tool call."
                    )
                )
            ]
        }

graph = StateGraph(AgentState)


graph.add_node("planner", plan_mode_ai)
graph.add_node("model_call",model_call)
graph.add_node("reflect",reflect)
tool_node = ToolNode(tools=TOOLS)
graph.add_node("tools",tool_node)


graph.set_entry_point("planner")

graph.add_conditional_edges(
    "model_call",
    should_continue,
    {
        "continue": "tools",
        "end": END,
        "reflect": "reflect",
    }
)

graph.add_edge("planner","model_call")
graph.add_edge("tools","model_call")
graph.add_edge("reflect","model_call")


app = graph.compile()