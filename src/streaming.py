"""Turn an async text stream into SSE using the library's native JSON events."""
import logging
from collections.abc import AsyncIterator
from contextlib import aclosing

from sse_starlette import EventSourceResponse, JSONServerSentEvent

logger = logging.getLogger(__name__)


def sse_response(tokens: AsyncIterator[str]) -> EventSourceResponse:
    async def events():
        try:
            async with aclosing(tokens):
                async for text in tokens:
                    yield JSONServerSentEvent(event="token", data={"text": text})
            yield JSONServerSentEvent(event="done", data={"status": "complete"})
        except Exception:
            logger.exception("Chat stream failed")
            yield JSONServerSentEvent(
                event="error", data={"message": "Unable to complete the chat request."},
            )

    # EventSourceResponse supplies heartbeats and disconnect cancellation.
    return EventSourceResponse(events(), send_timeout=30, headers={"X-Accel-Buffering": "no"})
