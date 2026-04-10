# PROVIDERS.md — Model Provider Abstraction

## Overview

Jarvis is model-agnostic. The LLM provider is controlled entirely via `.env` vars.
Swapping from Gemini to Claude to Ollama requires zero code changes.

The abstraction lives in `backend/providers/`.

---

## How It Works

Every provider implements the same `BaseProvider` interface.
The agent loop only ever talks to `BaseProvider` — it has no idea what's underneath.

```
Agent Loop
    ↓
BaseProvider (abstract)
    ├── ClaudeProvider      (Anthropic API)
    ├── OpenAIProvider      (OpenAI API / GPT-4o)
    ├── GeminiProvider      (Google Gemini API)
    ├── GroqProvider        (Groq API — fast + free tier)
    └── OllamaProvider      (Local — Ollama)
```

---

## Provider Interface

```python
# backend/providers/base.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator

class Message(TypedDict):
    role: str      # "user" | "assistant" | "tool"
    content: str

class ToolCall(TypedDict):
    id: str
    name: str
    input: dict

class ProviderResponse(TypedDict):
    text: str | None
    tool_calls: list[ToolCall]
    finish_reason: str   # "stop" | "tool_use" | "length"

class BaseProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        system: str,
        tools: list[dict],       # JSON Schema tool definitions
        stream: bool = False,
    ) -> ProviderResponse:
        """Single completion. Returns text or tool_calls."""
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[Message],
        system: str,
        tools: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Streaming completion. Yields text tokens."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for memory storage."""
        ...
```

---

## Environment Config

```bash
# backend/.env

# ── Active Provider ─────────────────────────────────────
# Options: claude | openai | gemini | groq | ollama
LLM_PROVIDER=gemini

# ── Model per Provider ──────────────────────────────────
CLAUDE_MODEL=claude-sonnet-4-6
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.0-flash
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# ── API Keys ────────────────────────────────────────────
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
# Ollama needs no key — it's local

# ── Embeddings ──────────────────────────────────────────
# Options: openai | gemini | ollama
# Use ollama for fully free/local embeddings
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text   # pull via: ollama pull nomic-embed-text

# ── Voice ───────────────────────────────────────────────
ELEVENLABS_API_KEY=        # leave blank to use pyttsx3 fallback
WHISPER_MODEL=base

# ── Database ────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis
```

---

## Provider Implementations

### Claude (Anthropic)
```python
# backend/providers/claude.py
import anthropic

class ClaudeProvider(BaseProvider):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def chat(self, messages, system, tools, stream=False):
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=messages,
            tools=tools or [],
        )
        return ProviderResponse(
            text=response.content[0].text if response.stop_reason == "end_turn" else None,
            tool_calls=[
                ToolCall(id=b.id, name=b.name, input=b.input)
                for b in response.content if b.type == "tool_use"
            ],
            finish_reason="tool_use" if response.stop_reason == "tool_use" else "stop",
        )
```

### OpenAI (GPT-4o)
```python
# backend/providers/openai.py
from openai import AsyncOpenAI

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def chat(self, messages, system, tools, stream=False):
        all_messages = [{"role": "system", "content": system}] + messages
        # Convert JSON Schema tools to OpenAI format
        oai_tools = [{"type": "function", "function": t} for t in tools]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            tools=oai_tools or None,
        )
        msg = response.choices[0].message
        return ProviderResponse(
            text=msg.content,
            tool_calls=[
                ToolCall(id=tc.id, name=tc.function.name, input=json.loads(tc.function.arguments))
                for tc in (msg.tool_calls or [])
            ],
            finish_reason="tool_use" if msg.tool_calls else "stop",
        )
```

### Gemini (Google)
```python
# backend/providers/gemini.py
import google.generativeai as genai

class GeminiProvider(BaseProvider):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    # Gemini has its own tool format — convert from JSON Schema
    # See: https://ai.google.dev/api/generate-content#tool_config
```

### Groq
```python
# backend/providers/groq.py
# Groq uses OpenAI-compatible API — reuse OpenAIProvider with different base_url
from openai import AsyncOpenAI

class GroqProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = settings.GROQ_MODEL
    # rest is identical to OpenAIProvider
```

### Ollama (Local)
```python
# backend/providers/ollama.py
# Ollama also exposes OpenAI-compatible API
from openai import AsyncOpenAI

class OllamaProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key="ollama",   # dummy key
            base_url=f"{settings.OLLAMA_BASE_URL}/v1"
        )
        self.model = settings.OLLAMA_MODEL

    # NOTE: Tool calling on 8B models is unreliable.
    # If tools keep failing, set tools=[] and handle manually in the agent loop.
```

---

## Provider Factory

```python
# backend/providers/__init__.py

from .base import BaseProvider
from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .ollama import OllamaProvider

def get_provider() -> BaseProvider:
    match settings.LLM_PROVIDER:
        case "claude":  return ClaudeProvider()
        case "openai":  return OpenAIProvider()
        case "gemini":  return GeminiProvider()
        case "groq":    return GroqProvider()
        case "ollama":  return OllamaProvider()
        case _: raise ValueError(f"Unknown provider: {settings.LLM_PROVIDER}")

# Singleton — instantiated once at startup
provider: BaseProvider = get_provider()
```

The agent loop imports `provider` from here. That's it.

---

## Embeddings

Embeddings are used for semantic memory (pgvector).
They're also abstracted — swap freely.

| Provider | Model | Cost | Notes |
|---|---|---|---|
| `ollama` | `nomic-embed-text` | Free | Pull once, runs locally |
| `openai` | `text-embedding-3-small` | ~$0.02/MTok | Very cheap, high quality |
| `gemini` | `text-embedding-004` | Free tier | Good quality |

**Recommended:** `ollama` with `nomic-embed-text` — free, fast, good enough.

```bash
ollama pull nomic-embed-text
```

---

## Tool Calling Compatibility

Not all providers handle tools equally well:

| Provider | Tool Calling | Notes |
|---|---|---|
| Claude | ✅ Excellent | Most reliable, best at chaining |
| GPT-4o | ✅ Excellent | Reliable, well-documented |
| Gemini 2.0 Flash | ✅ Good | Free tier, solid tool use |
| Groq (Llama 70B) | ⚠️ Decent | Works, occasional misses |
| Ollama 8B | ❌ Unreliable | Fine for chat, breaks on complex tool chains |

**If you're on Ollama and tools keep failing:** set `OLLAMA_TOOL_CALLING=false` in env.
The agent loop will detect this and fall back to a ReAct-style prompt where the model
reasons in plain text and we parse the action manually. Slower but more reliable.

---

## Swapping Provider — Checklist

1. Set `LLM_PROVIDER=<provider>` in `.env`
2. Set the corresponding `*_API_KEY` and `*_MODEL`
3. Restart backend: `uvicorn main:app --reload`
4. That's it. Nothing else changes.

If switching to Ollama for the first time:
```bash
ollama serve           # start ollama daemon
ollama pull llama3.1   # pull the model (one time)
ollama pull nomic-embed-text  # pull embedding model
```
