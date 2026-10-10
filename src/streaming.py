"""Adapt an async text stream to SSE with OpenAI-style event names."""
import logging
from collections.abc import AsyncIterator
from contextlib import aclosing

from sse_starlette import EventSourceResponse, JSONServerSentEvent

logger = logging.getLogger(__name__)


def sse_response(tokens: AsyncIterator[str]) -> EventSourceResponse:
    async def events():
        text_parts = []
        try:
            async with aclosing(tokens):
                yield JSONServerSentEvent(event="response.created", data={"status": "in_progress"})
                async for text in tokens:
                    text_parts.append(text)
                    yield JSONServerSentEvent(event="response.output_text.delta", data={"delta": text})
            yield JSONServerSentEvent(event="response.output_text.done", data={"text": "".join(text_parts)})
            yield JSONServerSentEvent(event="response.completed", data={"status": "completed"})
        except Exception:
            logger.exception("Chat stream failed")
            yield JSONServerSentEvent(
                event="response.failed", data={"message": "Unable to complete the chat request."},
            )

    # The SSE library handles framing, heartbeats, buffering headers, and disconnects.
    return EventSourceResponse(events(), send_timeout=30)
