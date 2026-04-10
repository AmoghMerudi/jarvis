# CLAUDE.md — Jarvis Personal AI Assistant

## Project Overview
A local-first personal AI assistant with voice, memory, and tool integrations.
Named "Jarvis" internally. Built for a single user. Privacy-first, runs entirely on local machine.

---

## Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Voice UI**: Web Speech API + custom audio visualizer
- **State**: Zustand
- **API calls**: fetch with custom hooks (no axios)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **LLM**: Model-agnostic — swap via `LLM_PROVIDER` env var (see PROVIDERS.md)
  - Supported: `claude` | `openai` | `gemini` | `groq` | `ollama`
  - Default: `gemini` (free tier, reliable tool calling)
- **Provider Abstraction**: `backend/providers/` — one interface, multiple implementations
- **Agent Orchestration**: Raw tool-calling loop (no LangChain)
- **Voice STT**: OpenAI Whisper (local, via whisper Python package)
- **Voice TTS**: ElevenLabs API (falls back to pyttsx3 if no key)
- **Memory**: Postgres + pgvector (semantic) + simple facts table (explicit)
- **Embeddings**: Ollama `nomic-embed-text` (free, local) — swappable via `EMBEDDING_PROVIDER`
- **Background Scheduler**: APScheduler — proactive alerts, deadline detection
- **Task Queue**: None for now — async FastAPI is sufficient

### Database
- **Postgres** via Docker (local)
- **pgvector** extension for semantic memory
- **Alembic** for migrations

### Infrastructure
- **Local only** — no cloud deployment
- **Docker Compose** for Postgres + pgvector
- **Uvicorn** for FastAPI dev server
- **Next.js dev server** for frontend

---

## Project Structure

```
jarvis/
├── CLAUDE.md
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt
│   ├── alembic/                 # DB migrations
│   │
│   ├── providers/               # Model-agnostic LLM abstraction
│   │   ├── __init__.py          # Factory: get_provider() + singleton
│   │   ├── base.py              # BaseProvider interface
│   │   ├── claude.py
│   │   ├── openai.py
│   │   ├── gemini.py
│   │   ├── groq.py
│   │   └── ollama.py
│   │
│   ├── agent/
│   │   ├── loop.py              # Core agent loop
│   │   ├── tools.py             # Tool registry
│   │   └── prompts.py           # System prompts
│   │
│   ├── memory/
│   │   ├── semantic.py          # pgvector search + store
│   │   └── facts.py             # Explicit key-value memory
│   │
│   ├── tools/                   # One file per tool
│   │   ├── calendar.py
│   │   ├── email.py             # Gmail API
│   │   ├── web_search.py
│   │   ├── files.py
│   │   └── system.py
│   │
│   ├── scheduler/
│   │   └── jobs.py              # APScheduler — deadline alerts, reminders
│   │
│   ├── voice/
│   │   ├── stt.py               # Whisper STT
│   │   └── tts.py               # ElevenLabs / pyttsx3 fallback
│   │
│   └── db/
│       ├── connection.py
│       └── models.py
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main chat UI
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── Chat.tsx
│   │   ├── VoiceButton.tsx
│   │   └── AudioVisualizer.tsx
│   │
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useVoice.ts
│   │
│   └── lib/
│       └── api.ts               # Backend API client
```

---

## Core Concepts

### Agent Loop
The agent loop lives in `backend/agent/loop.py`. It:
1. Takes user message + conversation history
2. Retrieves relevant memories
3. Calls Claude with system prompt + tools
4. If Claude calls a tool → execute it → feed result back → continue loop
5. Returns final text response

**Never break this loop into scattered files.** Keep it tight and readable.

### Tool Calling
Tools are plain Python async functions registered in `backend/agent/tools.py`.
Each tool has:
- A name
- A description (used in system prompt)
- An input schema (JSON Schema)
- An `execute(input) -> str` method

Claude decides which tools to call. We don't hardcode routing.

### Memory
Two types:
1. **Semantic memory** — conversation summaries + important moments stored as embeddings. Retrieved by cosine similarity.
2. **Explicit facts** — structured key-value store. e.g. `{"user_name": "Aryan", "preferred_wake_time": "7am"}`. Updated when user tells Jarvis something factual about themselves.

On every request: retrieve top-5 semantic memories + all explicit facts → inject into system prompt.

---

## Code Style

### Python
- Type hints everywhere — no exceptions
- Async/await throughout (FastAPI + asyncpg)
- Pydantic models for all request/response shapes
- No global mutable state
- Functions over classes unless state is genuinely needed
- Keep files under 200 lines — split if bigger

### TypeScript / Next.js
- Strict TypeScript — no `any`
- Functional components only
- Custom hooks for all logic — components are dumb
- No inline styles — Tailwind only
- API calls only in hooks or lib/api.ts — never in components

### General
- No premature abstraction — build the simple thing first
- No unused imports
- Descriptive variable names — no single-letter vars outside loops
- Comments explain *why*, not *what*

---

## Environment Variables

```bash
# backend/.env

# ── Active Provider (only change this to swap models) ───
# Options: claude | openai | gemini | groq | ollama
LLM_PROVIDER=gemini

# ── Model per provider ──────────────────────────────────
CLAUDE_MODEL=claude-sonnet-4-6
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.0-flash
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# ── API Keys (fill only the one you're using) ───────────
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
# Ollama: no key needed

# ── Embeddings (free local default) ────────────────────
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text

# ── Voice ───────────────────────────────────────────────
ELEVENLABS_API_KEY=        # leave blank to use pyttsx3 fallback
WHISPER_MODEL=base

# ── Database ────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Dev Commands

```bash
# Start DB
docker-compose up -d

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Run DB migrations
cd backend
alembic upgrade head
```

---

## Dos and Don'ts

**Do:**
- Keep the agent loop pure and readable
- Add new capabilities as tools
- Test tools in isolation before wiring to agent
- Store useful facts Jarvis learns about the user
- Use streaming responses for chat (SSE from FastAPI → frontend)

**Don't:**
- Use LangChain or any heavy orchestration framework
- Store raw conversation history in memory (summarize instead)
- Add cloud dependencies — this is local only
- Over-engineer memory — simple is fine to start
- Build LLM-native features as tools (games, jokes, unit conversions — LLM does these)
- Send emails without explicit user confirmation in agent loop
- Delete files without `confirmed=true` in tool input

---

## Current Build Phases

- [ ] Phase 0: Project setup (repo, Docker, DB, Next.js scaffold)
- [ ] Phase 1: Bare agent loop + basic chat
- [ ] Phase 2: Provider abstraction (Claude, OpenAI, Gemini, Groq, Ollama)
- [ ] Phase 3: Memory (pgvector semantic + explicit facts)
- [ ] Phase 4: Voice (Whisper STT + ElevenLabs/pyttsx3 TTS)
- [ ] Phase 5A: System & network tools (battery, RAM, IP, speedtest, screenshot)
- [ ] Phase 5B: File & image tools (organize, compress, PDF, Imgur)
- [ ] Phase 5C: Weather (Open-Meteo, free)
- [ ] Phase 5D: Sports (API-Sports free tier)
- [ ] Phase 5E: Health & fitness (BMI, nutrition, workouts)
- [ ] Phase 5F: Email + Calendar (Gmail + Google Calendar OAuth2)
- [ ] Phase 6: Proactive scheduler (APScheduler — deadline alerts, morning briefing)
- [ ] Phase 7: LLM-native features (games, calculations, conversions, QR, translate)
- [ ] Phase 8: UI polish (sidebar, notifications, settings panel, onboarding)
- [ ] Phase 9: Hardening (retries, error handling, tests, logging)

See ROADMAP.md for full task breakdown per phase.
