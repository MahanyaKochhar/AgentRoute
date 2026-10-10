"""FastAPI entrypoint: uvicorn src.main:app --reload."""
from fastapi import FastAPI

from src.resource import resource

app = FastAPI(title="Stream")
app.include_router(resource.router)
