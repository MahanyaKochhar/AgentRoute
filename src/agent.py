"""Construct the configured LangChain agent separately from the service."""
from langchain.agents import create_agent

from src.middleware import select_tools
from src.navigator_llm import get_llm
from src.settings import Settings
from src.state import ChatState
from src.tools import HEALTHCARE_TOOLS


def build_agent(*, use_decisions: bool = True):
    settings = Settings()
    return create_agent(
        model=get_llm(settings),
        tools=HEALTHCARE_TOOLS,
        middleware=[select_tools] if use_decisions else [],
        state_schema=ChatState,
        system_prompt=(
            "You are Stream, a healthcare public-data assistant. "
            "Use the available relevant tools when needed. "
            "In your final response, list the exact names of the tools you actually called, "
            "based on tool calls and tool messages in this conversation. Do not list tools "
            "merely because they were available. If you called no tools, say so. "
            "Explicitly state: 'These tools are static tools for now and return placeholder "
            "data. Tool routing is implemented, but live data retrieval is not connected yet.' "
            "Explain briefly what each called tool is intended to retrieve. "
            "Do not claim that real searches ran, real studies were found, or results are "
            "extensive: placeholder responses contain no retrieved records. "
            "Identify these results as placeholders and never invent clinical studies, "
            "citations, drug facts, coverage decisions, or provider records. "
            "If no tool is relevant, answer the user's message directly."
        ),
    )
