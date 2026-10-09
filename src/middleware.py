"""Decorator-style Jev routing with all relevance questions evaluated together."""
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import (
    ExtendedModelResponse, ModelRequest, ModelResponse, wrap_model_call,
)
from langchain_typesafe import Noul, TypeSafeClassifier
from langgraph.types import Command

from src.settings import Settings
from src.state import ChatState
from src.tools import HEALTHCARE_TOOLS

QUESTIONS = {
    tool.name: Noul(instructions=(
        "Would this tool be useful to answer the user's request? "
        f"Tool: {tool.name}. Capabilities: {tool.description}"
    ))
    for tool in HEALTHCARE_TOOLS
}


@wrap_model_call(state_schema=ChatState)
async def select_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
) -> ExtendedModelResponse:
    settings = Settings()
    scores = request.state.get("tool_scores")
    if scores is None:
        classifier = TypeSafeClassifier(
            model=settings.jev_model, timeout=settings.jev_timeout_seconds,
        )
        result = await classifier.ainvoke({
            "state": request.state["request"], "questions": QUESTIONS,
        })
        scores = {name: result.nouls[name].noul for name in QUESTIONS}

    selected = [tool for tool in request.tools if scores[tool.name] >= settings.tool_threshold]
    response = await handler(request.override(tools=selected))
    return ExtendedModelResponse(response, Command(update={"tool_scores": scores}))
