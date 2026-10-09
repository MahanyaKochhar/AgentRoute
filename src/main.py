"""FastAPI entrypoint: uvicorn src.main:app --reload."""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.resource import router
from src.service import ChatService


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    app.state.chat_service = ChatService()
    yield


app = FastAPI(title="Stream", lifespan=lifespan)
app.include_router(router)
