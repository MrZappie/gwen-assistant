from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated

class AgentState(TypedDict):
    user_input: str
    messages: Annotated[List[BaseMessage], add_messages]

    conversation_summary: str  # NEW

    plan: List[Dict[str, Any]]
    current_step: int
    observations: List[str]
    done: bool
