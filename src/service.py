"""The chat service owns the agent and streams its response text."""
from collections.abc import AsyncIterator
from contextlib import aclosing
import logging
from time import perf_counter
from uuid import uuid4

from langchain_core.messages import AIMessageChunk

from src.agent import build_agent
from src.metrics import RequestMetrics, current_metrics
from src.settings import Settings
from src.tools import HEALTHCARE_TOOLS

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, *, use_decisions: bool = False):
        self.approach = "decisions" if use_decisions else "all_tools"
        self.model = Settings().navigator_model
        self.agent = build_agent(use_decisions=use_decisions)

    async def stream(self, message: str, request_id: str | None = None) -> AsyncIterator[str]:
        metrics = RequestMetrics(request_id or str(uuid4()), self.approach, self.model)
        token = current_metrics.set(metrics)
        status = "cancelled"
        try:
            if self.approach == "all_tools":
                metrics.selected_tools = [tool.name for tool in HEALTHCARE_TOOLS]
                logger.info("tools.selected names=%s", metrics.selected_tools)
            async with aclosing(self.agent.astream(
                {"request": message, "messages": [{"role": "user", "content": message}]},
                stream_mode="messages", config={"callbacks": [metrics]},
            )) as stream:
                async for chunk, metadata in stream:
                    if isinstance(chunk, AIMessageChunk) and metadata.get("langgraph_node") == "model" and chunk.text:
                        if metrics.first_text_ms is None:
                            metrics.first_text_ms = round((perf_counter() - metrics.started) * 1000, 2)
                        yield chunk.text
            status = "completed"
        except Exception:
            status = "failed"
            logger.exception("Chat stream failed")
            raise
        finally:
            metrics.finish(status)
            current_metrics.reset(token)
