"""The chat resource owns its service and exposes POST /chat."""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sse_starlette import EventSourceResponse

from src.service import ChatService
from src.streaming import sse_response


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=20000)


class ChatResource:
    def __init__(self):
        self.service: ChatService
        self.router = APIRouter()
        self.router.add_api_route(
            "/chat", self.chat, methods=["POST"], response_class=EventSourceResponse,
            responses={200: {"content": {"text/event-stream": {}}}},
        )

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        load_dotenv()
        self.service = ChatService()
        yield

    async def chat(self, payload: ChatRequest) -> EventSourceResponse:
        return sse_response(self.service.stream(payload.message))


resource = ChatResource()
