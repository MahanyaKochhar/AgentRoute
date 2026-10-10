from langchain.agents import AgentState
from typing_extensions import NotRequired


class ChatState(AgentState):
    """Per-run state: inherited messages, original request, and cached routing scores."""
    request: str
    tool_scores: NotRequired[dict[str, float]]
