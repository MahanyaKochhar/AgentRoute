"""The chat service owns the agent and streams its response text."""
from collections.abc import AsyncIterator
from contextlib import aclosing

from langchain_core.messages import AIMessageChunk

from src.agent import build_agent


class ChatService:
    def __init__(self):
        self.agent = build_agent()

    async def stream(self, message: str) -> AsyncIterator[str]:
        async with aclosing(self.agent.astream(
            {"request": message, "messages": [{"role": "user", "content": message}]},
            stream_mode="messages",
        )) as stream:
            async for chunk, metadata in stream:
                if isinstance(chunk, AIMessageChunk) and metadata.get("langgraph_node") == "model" and chunk.text:
                    yield chunk.text
