"""Construct the configured LangChain agent separately from the service."""
from langchain.agents import create_agent

from src.middleware import select_tools
from src.navigator_llm import get_llm
from src.settings import Settings
from src.state import ChatState
from src.tools import HEALTHCARE_TOOLS


def build_agent():
    settings = Settings()
    return create_agent(
        model=get_llm(settings),
        tools=HEALTHCARE_TOOLS,
        middleware=[select_tools],
        state_schema=ChatState,
        system_prompt=(
            "You are Stream, a healthcare public-data assistant. "
            "Use the available relevant tools when needed. "
            "All tools currently return static demonstration strings, not live data. "
            "Identify these results as placeholders and never invent clinical studies, "
            "citations, drug facts, coverage decisions, or provider records. "
            "If no tool is relevant, answer the user's message directly."
        ),
    )
