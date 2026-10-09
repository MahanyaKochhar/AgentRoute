from langchain.agents import AgentState
from typing_extensions import NotRequired


class ChatState(AgentState):
    request: str
    tool_scores: NotRequired[dict[str, float]]
