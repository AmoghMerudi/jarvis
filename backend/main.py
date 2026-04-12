import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.loop import run_agent
from agent.tools import load_all_tools
from db.connection import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_tools()
    try:
        await init_db()
    except Exception as exc:
        logger.warning("DB unavailable on startup — continuing without it: %s", exc)
    yield


app = FastAPI(title="Jarvis", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, Any]] = []


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await run_agent(request.message, request.history)
    return ChatResponse(reply=reply)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
