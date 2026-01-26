import json
import uuid
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ai.models.state import AgentState
from ai.agent.model import get_model
from ai.tools.tool_registry import TOOLS

# Tool lookup for executor
TOOL_REGISTRY: Dict[str, Any] = {tool.name: tool for tool in TOOLS}

# --- PROMPTS ---
PLANNER_PROMPT = """
You are a planning agent.
Given a user request and past observations, produce a minimal,
step-by-step plan using available tools.

Rules:
- Output ONLY valid JSON
- Each step must include: action, arguments, reason
- Do NOT execute tools
- Do NOT repeat completed work
"""

JUDGE_PROMPT = """
You are a judge agent.
Decide if the user's request is satisfied using ONLY the observations.

Rules:
- Output ONLY valid JSON
- If satisfied: { "satisfied": true }
- If not: { "satisfied": false, "feedback": "<what is missing>" }
"""

# --- NODES ---
def planner_node(state: AgentState) -> AgentState:
    """Generate a plan internally; user never sees this directly."""
    model = get_model(bind=True)
    user_input = state.get("user_input", "")
    observations = state.get("observations", [])

    response = model.invoke([
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=f"User request: {user_input}\nPrevious observations: {observations}")
    ])

    try:
        plan = json.loads(response.content)
        if not isinstance(plan, list):
            plan = []
    except Exception:
        plan = []

    return {
        "plan": plan,
        "current_step": 0,
        "observations": observations,
        "user_input": user_input
    }

def executor_node(state: AgentState) -> AgentState:
    """Execute tools, track observations internally."""
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    observations = state.get("observations", [])
    user_input = state.get("user_input", "")

    if not plan or current_step >= len(plan):
        return {
            "observations": observations,
            "current_step": current_step,
            "user_input": user_input
        }

    step = plan[current_step]
    action = step.get("action", "")
    arguments = step.get("arguments", {})

    if action not in TOOL_REGISTRY:
        observation = f"Unknown action requested: {action}"
    else:
        tool = TOOL_REGISTRY[action]
        result = tool.invoke(arguments)
        text = str(result)
        if len(text) > 2000:
            text = text[:2000] + "...(truncated)"
        observation = f"{action}({arguments}) -> {text}"

    return {
        "observations": observations + [observation],
        "current_step": current_step + 1,
        "user_input": user_input
    }

def judge_node(state: AgentState) -> AgentState:
    """Judge if the task is complete internally; feedback stays internal."""
    model = get_model(bind=False)
    observations = state.get("observations", [])
    user_input = state.get("user_input", "")

    response = model.invoke([
        SystemMessage(content=JUDGE_PROMPT),
        HumanMessage(content=f"User request: {user_input}\nObservations: {observations}")
    ])

    try:
        verdict = json.loads(response.content)
    except Exception:
        verdict = {"satisfied": False, "feedback": "Unable to parse verdict."}

    done = verdict.get("satisfied", False)
    feedback = verdict.get("feedback", "") if not done else ""

    return {
        "done": done,
        "feedback": feedback,
        "observations": observations,
        "user_input": user_input
    }

def chatter_node(state: AgentState) -> AgentState:
    """
    Generates a friendly, human-like AI response for the user.
    Uses internal observations and optional feedback to form a natural reply.
    """
    model = get_model(bind=False)
    user_input = state.get("user_input", "")
    observations = state.get("observations", [])
    feedback = state.get("feedback", "")
    done = state.get("done", False)

    # Combine observations and feedback into context
    context = observations.copy()
    if feedback:
        context.append(f"Feedback: {feedback}")

    prompt_text = f"""
You are a friendly AI assistant. Respond to the user's request naturally.
User input: {user_input}
Internal observations and feedback: {context}

Provide a concise, helpful, and human-friendly response. Do NOT mention plans or tasks.
    """

    response = model.invoke([
        HumanMessage(content=prompt_text)
    ])

    ai_msg = AIMessage(content=response.content.strip(), id=str(uuid.uuid4()))

    return {
        "messages": [ai_msg],
        "observations": observations,
        "user_input": user_input
    }

# --- GRAPH ---
graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("judge", judge_node)
graph.add_node("chatter", chatter_node)

graph.set_entry_point("planner")

# planner → executor
graph.add_edge("planner", "executor")

# executor loops until plan exhausted
graph.add_conditional_edges(
    "executor",
    lambda s: "judge" if s.get("current_step", 0) >= len(s.get("plan", [])) else "executor",
    {"executor": "executor", "judge": "judge"}
)

# judge → chatter
graph.add_conditional_edges(
    "judge",
    lambda s: "chatter" if s.get("done") or s.get("feedback") else "planner",
    {"chatter": "chatter", "planner": "planner"}
)

# chatter → END
graph.add_edge("chatter", END)

# --- COMPILE ---
app = graph.compile()
