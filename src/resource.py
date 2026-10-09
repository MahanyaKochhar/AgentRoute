"""POST /chat resource: validate the message and stream the service response."""
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field
from sse_starlette import EventSourceResponse

from src.streaming import sse_response

router = APIRouter()


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=20000)


@router.post("/chat", response_class=EventSourceResponse,
             responses={200: {"content": {"text/event-stream": {}}}})
async def chat(payload: ChatRequest, request: Request) -> EventSourceResponse:
    return sse_response(request.app.state.chat_service.stream(payload.message))
