"""Expose the all-tools and Decisions agents with the same SSE contract."""
from collections.abc import AsyncIterator, Callable
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from sse_starlette import EventSourceResponse

from src.service import ChatService
from src.streaming import sse_response


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=20000)


class ChatResource:
    def __init__(self):
        self.service = ChatService()
        self.router = APIRouter()


load_dotenv()
resource = ChatResource()


@resource.router.post(
    "/chat", response_class=EventSourceResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def chat(payload: ChatRequest) -> EventSourceResponse:
    return chat_response(resource.service.stream, payload.message)


def chat_response(stream: Callable[[str, str], AsyncIterator[str]], message: str) -> EventSourceResponse:
    request_id = str(uuid4())
    response = sse_response(stream(message, request_id))
    response.headers["X-Request-ID"] = request_id
    return response


@resource.router.post(
    "/v1/chat", response_class=EventSourceResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def routed_chat(payload: ChatRequest) -> EventSourceResponse:
    return chat_response(resource.service.stream_routed, payload.message)
