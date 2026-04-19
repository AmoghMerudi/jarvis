import logging
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, Any]] = []


class ChatResponse(BaseModel):
    reply: str
    stop_reason: str
    usage: dict[str, int]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await run_agent(request.message, request.history)
    return ChatResponse(
        reply=result.output,
        stop_reason=result.stop_reason,
        usage={
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens,
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
