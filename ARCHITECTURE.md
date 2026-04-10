# ARCHITECTURE.md — Jarvis System Design

## How It All Fits Together

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                 │
│                                                     │
│   ┌──────────┐    ┌─────────────┐    ┌───────────┐  │
│   │ Chat UI  │    │ Voice Button│    │  Audio    │  │
│   │          │    │  (record)   │    │ Visualizer│  │
│   └────┬─────┘    └──────┬──────┘    └───────────┘  │
│        │                 │                          │
│        └────────┬─────────┘                         │
│                 │ HTTP / SSE                        │
└─────────────────┼───────────────────────────────────┘
                  │
┌─────────────────┼───────────────────────────────────┐
│                 ▼      BACKEND (FastAPI)             │
│                                                     │
│   ┌─────────────────────────────────────────────┐   │
│   │              Agent Loop                     │   │
│   │                                             │   │
│   │  1. Receive message                         │   │
│   │  2. Fetch memories                          │   │
│   │  3. Build prompt                            │   │
│   │  4. Call Claude API ──────────────────────► │   │
│   │  5. Claude returns text OR tool_call        │   │
│   │  6. If tool_call → execute → back to step 4 │   │
│   │  7. Stream final response to frontend       │   │
│   └──────────────────────────────────────────┬──┘   │
│                                              │      │
│   ┌──────────────┐    ┌──────────────────┐   │      │
│   │ Memory Layer │    │   Tool Layer     │◄──┘      │
│   │              │    │                  │          │
│   │ - pgvector   │    │ - calendar       │          │
│   │ - facts DB   │    │ - web_search     │          │
│   └──────┬───────┘    │ - files          │          │
│          │            │ - system         │          │
│   ┌──────▼───────┐    └──────────────────┘          │
│   │  PostgreSQL  │                                  │
│   │  + pgvector  │                                  │
│   └──────────────┘                                  │
│                                                     │
│   ┌──────────────┐    ┌──────────────────┐          │
│   │  Voice / STT │    │   Voice / TTS    │          │
│   │  (Whisper)   │    │  (ElevenLabs)    │          │
│   └──────────────┘    └──────────────────┘          │
└─────────────────────────────────────────────────────┘
```

---

## Request Lifecycle

### Text Message
1. User types message in Next.js UI
2. Frontend sends `POST /chat` with `{message, conversation_id}`
3. FastAPI receives, kicks off agent loop
4. Agent fetches relevant memories from pgvector
5. Agent builds system prompt (memories + facts + tools list)
6. Agent calls Claude API with full context
7. Claude responds with text → streamed back via SSE
8. Frontend renders response token by token
9. After response: summarize + store in memory async

### Voice Message
1. User holds voice button → browser records audio
2. On release → audio blob sent to `POST /voice/transcribe`
3. Whisper transcribes → returns text
4. Same flow as text message from step 2
5. Response text sent to `POST /voice/speak`
6. ElevenLabs generates audio → streamed back
7. Frontend plays audio

---

## Memory Design

### Semantic Memory (pgvector)
```sql
CREATE TABLE memories (
  id UUID PRIMARY KEY,
  content TEXT,           -- The memory text
  embedding VECTOR(1536), -- text-embedding-3-small
  created_at TIMESTAMPTZ,
  importance FLOAT        -- 0-1, used for pruning later
);
```

What gets stored:
- Summaries of conversations (every N turns)
- Important decisions or events user mentions
- Things the user explicitly asks Jarvis to remember

Retrieval: embed the current user message → cosine similarity search → top 5 results injected into system prompt.

### Explicit Facts (key-value)
```sql
CREATE TABLE facts (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMPTZ
);
```

Examples:
- `user_name` → `"Aryan"`
- `preferred_language` → `"English"`
- `timezone` → `"America/Toronto"`
- `wake_time` → `"7:00 AM"`

All facts injected into every system prompt — they're small, always relevant.

---

## Tool Design

Each tool follows this interface:

```python
class Tool:
    name: str
    description: str          # Claude reads this to decide when to use it
    input_schema: dict        # JSON Schema
    
    async def execute(self, input: dict) -> str:
        ...                   # Returns string result
```

Tools are registered in a central registry. The agent loop passes tool definitions to Claude and routes tool calls back to the right execute() function.

---

## Streaming

FastAPI streams responses using `StreamingResponse` + Server-Sent Events (SSE).

```
backend:  yield "data: {token}\n\n"
frontend: EventSource reads tokens → appends to UI in real time
```

---

## What's NOT in scope (yet)

- Proactive notifications (Jarvis talking to you without being asked)
- Multi-user support
- Mobile app
- Smart home integration
- Vision / image understanding
- Long-term task execution / scheduling
