# MEMORIES.md — Memory System Reference

## Overview

Jarvis has two memory systems working together. Neither is optional — they serve different purposes and complement each other.

---

## 1. Semantic Memory (pgvector)

### What it is
Long-term fuzzy memory. Stores text as vector embeddings. Retrieved by meaning, not exact match.

### What gets stored
- Conversation summaries (auto-generated every 10 turns)
- Explicit "remember this" requests from user
- Important events, decisions, facts mentioned in passing

### How retrieval works
1. Embed the current user message using `text-embedding-3-small`
2. Run cosine similarity search against all stored memories
3. Return top 5 most relevant
4. Inject into system prompt under `## What I Remember`

### Schema
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content     TEXT NOT NULL,
    embedding   VECTOR(1536) NOT NULL,
    source      TEXT,           -- 'conversation', 'explicit', 'summary'
    created_at  TIMESTAMPTZ DEFAULT now(),
    importance  FLOAT DEFAULT 0.5  -- reserved for future pruning
);

CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);
```

### Python interface
```python
# Store a memory
await store_memory(content="User prefers morning meetings", source="explicit")

# Retrieve relevant memories
memories = await search_memories(query="schedule a meeting", top_k=5)
```

---

## 2. Explicit Facts (key-value)

### What it is
Structured, always-present memory. Small facts that are always relevant regardless of context.

### What gets stored
Things that are true about the user as a person — preferences, identity, context.

### Schema
```sql
CREATE TABLE facts (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT now()
);
```

### Default facts to populate on first run
| Key | Example Value |
|-----|--------------|
| `user_name` | `"Aryan"` |
| `timezone` | `"America/Toronto"` |
| `preferred_language` | `"English"` |
| `wake_time` | `"7:00 AM"` |
| `occupation` | `"Full Stack Developer"` |

### Python interface
```python
# Set a fact
await set_fact("wake_time", "6:30 AM")

# Get all facts (returns dict)
facts = await get_all_facts()

# Get one fact
name = await get_fact("user_name")
```

---

## System Prompt Injection

Every request builds a context block like this:

```
## About You
- Name: Aryan
- Timezone: America/Toronto
- Occupation: Full Stack Developer
- Wake time: 7:00 AM

## Relevant Memories
- You prefer not to schedule meetings before 9am
- You're working on a personal AI assistant project
- Your laptop is a MacBook Pro M2
```

This block is prepended to the system prompt before every Claude call.

---

## Memory Lifecycle

```
Conversation happens
        ↓
Every 10 turns → summarize last 10 messages
        ↓
Store summary as semantic memory
        ↓
Old raw messages discarded (not stored)
        ↓
Only summaries + facts persist long-term
```

This keeps the memory store lean and the embeddings meaningful.

---

## Pruning (future)

Not implemented in Phase 1. When needed:
- Delete memories with `importance < 0.2` older than 90 days
- Merge similar memories (cosine similarity > 0.95)
- Cap total memories at 1000 before pruning kicks in
