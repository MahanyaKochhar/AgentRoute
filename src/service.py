"""One chat service owns both agents and streams their response text."""
from collections.abc import AsyncIterator
from contextlib import aclosing

from langchain_core.messages import AIMessageChunk
from langfuse.langchain import CallbackHandler

from src.agent import build_agent


class ChatService:
    def __init__(self):
        self.agent = build_agent(use_decisions=False)
        self.routed_agent = build_agent(use_decisions=True)

    def stream(self, message: str, request_id: str) -> AsyncIterator[str]:
        return self._stream(self.agent, "all_tools", message, request_id)

    def stream_routed(self, message: str, request_id: str) -> AsyncIterator[str]:
        return self._stream(self.routed_agent, "decisions", message, request_id)

    async def _stream(self, agent, approach: str, message: str,
                      request_id: str) -> AsyncIterator[str]:
        langfuse_handler = CallbackHandler(trace_context={"trace_id": request_id.replace("-", "")})
        # Keep callback span context in the task that executes the middleware.
        langfuse_handler.run_inline = True
        stream = agent.astream(
            {"request": message, "messages": [{"role": "user", "content": message}]},
            stream_mode="messages", config={
                "callbacks": [langfuse_handler], "run_id": request_id,
                "run_name": f"chat.{approach}.{request_id}", "tags": [approach],
                "metadata": {"approach": approach, "request_id": request_id},
            },
        )
        async with aclosing(stream):
            async for chunk, metadata in stream:
                if metadata.get("langgraph_node") == "model" and isinstance(chunk, AIMessageChunk) and chunk.text:
                    yield chunk.text
