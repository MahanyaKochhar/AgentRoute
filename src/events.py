"""OpenAI text-event types and a compact lifecycle summary for Stream."""
from typing import Literal

from openai.types.responses import ResponseTextDeltaEvent, ResponseTextDoneEvent
from pydantic import BaseModel


class ResponseError(BaseModel):
    code: str = "server_error"
    message: str = "Unable to complete the chat request."


class ResponseSummary(BaseModel):
    id: str
    status: Literal["in_progress", "completed", "failed"]
    error: ResponseError | None = None


class ResponseLifecycleEvent(BaseModel):
    type: Literal["response.created", "response.completed", "response.failed"]
    sequence_number: int
    response: ResponseSummary


StreamEvent = ResponseLifecycleEvent | ResponseTextDeltaEvent | ResponseTextDoneEvent
