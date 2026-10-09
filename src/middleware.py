"""Select tools with named OpenAI Decisions predicates over the user request."""
import math
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import (
    ExtendedModelResponse, ModelRequest, ModelResponse, wrap_model_call,
)
from langgraph.types import Command
from openai import AsyncOpenAI

from src.settings import Settings
from src.state import ChatState
from src.tools import HEALTHCARE_TOOLS

QUESTIONS = [
    {
        "type": "predicate",
        "name": tool.name,
        "instructions": (
            "Does answering the user's request require or benefit from this tool's "
            "specific capabilities? Evaluate relevance, not just a shared healthcare topic. "
            f"Tool: {tool.name}. Capabilities: {tool.description}"
        ),
    }
    for tool in HEALTHCARE_TOOLS
]


def predicate_scores(answers) -> dict[str, float]:
    """Accept a complete set of named predicates; refusals stop routing."""
    scores = {}
    for answer in answers:
        if answer.type != "predicate":
            raise ValueError(f"Decision did not return a predicate for {answer.name}.")
        if answer.name in scores:
            raise ValueError(f"Duplicate decision answer for {answer.name}.")
        if not math.isfinite(answer.probability) or not 0 <= answer.probability <= 1:
            raise ValueError(f"Invalid decision probability for {answer.name}.")
        scores[answer.name] = answer.probability
    if set(scores) != {question["name"] for question in QUESTIONS}:
        raise ValueError("Decision answers do not match the requested tools.")
    return scores


@wrap_model_call(state_schema=ChatState)
async def select_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
) -> ExtendedModelResponse:
    settings = Settings()
    scores = request.state.get("tool_scores")
    if scores is None:
        api_key = settings.openai_api_key.get_secret_value()
        if not api_key.strip():
            raise ValueError("OPENAI_API_KEY is required for Decisions tool routing.")
        async with AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            timeout=settings.decision_timeout_seconds,
            max_retries=2,
        ) as client:
            decision = await client.decisions.create(
                model=settings.decision_model,
                input=request.state["request"],
                questions=QUESTIONS,
            )
        scores = predicate_scores(decision.answers)

    selected = [tool for tool in request.tools if scores[tool.name] >= settings.tool_threshold]
    response = await handler(request.override(tools=selected))
    return ExtendedModelResponse(response, Command(update={"tool_scores": scores}))
