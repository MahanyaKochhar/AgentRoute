"""Adapt an async text stream to typed OpenAI-style SSE events."""
import logging
from collections.abc import AsyncIterator
from contextlib import aclosing
from itertools import count
from uuid import uuid4

from sse_starlette import EventSourceResponse, JSONServerSentEvent

from src.events import (
    ResponseError, ResponseLifecycleEvent, ResponseSummary,
    ResponseTextDeltaEvent, ResponseTextDoneEvent, StreamEvent,
)

logger = logging.getLogger(__name__)


def encode_event(event: StreamEvent) -> JSONServerSentEvent:
    return JSONServerSentEvent(event=event.type, data=event.model_dump(mode="json", exclude_none=True))


def sse_response(tokens: AsyncIterator[str]) -> EventSourceResponse:
    async def events():
        response_id, item_id = f"resp_{uuid4().hex}", f"msg_{uuid4().hex}"
        sequence = count()
        text_parts = []
        yield encode_event(ResponseLifecycleEvent(
            type="response.created", sequence_number=next(sequence),
            response=ResponseSummary(id=response_id, status="in_progress"),
        ))
        try:
            async with aclosing(tokens):
                async for text in tokens:
                    text_parts.append(text)
                    yield encode_event(ResponseTextDeltaEvent(
                        type="response.output_text.delta", sequence_number=next(sequence),
                        item_id=item_id, output_index=0, content_index=0, delta=text, logprobs=[],
                    ))
            yield encode_event(ResponseTextDoneEvent(
                type="response.output_text.done", sequence_number=next(sequence),
                item_id=item_id, output_index=0, content_index=0,
                text="".join(text_parts), logprobs=[],
            ))
            yield encode_event(ResponseLifecycleEvent(
                type="response.completed", sequence_number=next(sequence),
                response=ResponseSummary(id=response_id, status="completed"),
            ))
        except Exception:
            logger.exception("Chat stream failed")
            yield encode_event(ResponseLifecycleEvent(
                type="response.failed", sequence_number=next(sequence),
                response=ResponseSummary(id=response_id, status="failed", error=ResponseError()),
            ))

    # The SSE library handles framing, heartbeats, buffering headers, and disconnects.
    return EventSourceResponse(events(), send_timeout=30)
