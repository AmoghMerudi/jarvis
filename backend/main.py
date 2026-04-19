import logging
from contextlib import asynccontextmanager
from functools import partial
from typing import Any
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.loop import run_agent
from agent.tools import load_all_tools
from db.connection import init_db
from voice.stt import transcribe

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


@app.post("/voice/transcribe")
async def voice_transcribe(audio: UploadFile = File(...)) -> dict[str, str]:
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    filename = audio.filename or "audio.webm"
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "webm"

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, partial(transcribe, audio_bytes, extension))
    return {"text": text}


@app.get("/health")
async def health() -> dict[str, Any]:
    import os
    provider_name = os.getenv("LLM_PROVIDER", "unknown")
    model_map = {
        "claude": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        "openai": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "groq": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "ollama": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    }
    model = model_map.get(provider_name, "unknown")
    return {
        "status": "ok",
        "provider": provider_name,
        "model": model,
        "memory": True,
        "voice": True,
    }
