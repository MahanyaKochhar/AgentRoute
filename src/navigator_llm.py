"""LangChain chat adapter for the existing OpenAI-compatible Navigator gateway."""
from langchain_openai import ChatOpenAI

from src.settings import Settings


def get_llm(settings: Settings) -> ChatOpenAI:
    endpoint = settings.navigator_api_endpoint.rstrip("/")
    # Accept a base URL or full completion URL; retain the /v1 prefix.
    if endpoint.endswith("/chat/completions"):
        endpoint = endpoint.removesuffix("/chat/completions")
    return ChatOpenAI(
        api_key=settings.navigator_api_key,
        base_url=endpoint,
        model=settings.navigator_model,
        streaming=True,
        timeout=60,
        max_retries=2,
    )
