# ROADMAP.md — Jarvis Build Plan

## How to Read This

Each phase builds on the previous one. Don't skip phases.
Tasks within a phase can be done in any order unless marked with ↳ (depends on task above).

Estimated times assume you're working on this part-time (evenings/weekends).
If you're going full-time on it, cut estimates in half.

---

## Phase 0 — Project Setup
**Goal:** Repo is scaffolded, environment works, you can run the project.
**Time:** 2–4 hours

- [ ] Create monorepo: `jarvis/backend/` and `jarvis/frontend/`
- [ ] Init git repo, add `.gitignore` (exclude `.env`, `__pycache__`, `.next`, `node_modules`)
- [ ] Write `docker-compose.yml` for Postgres + pgvector
  - ↳ Test: `docker-compose up -d` runs without errors
- [ ] Create `backend/.env` from `.env.example`, fill in at least one LLM provider key
- [ ] Set up Python venv, install base deps (`fastapi`, `uvicorn`, `pydantic`, `asyncpg`, `alembic`)
- [ ] Set up Next.js 14 with TypeScript + Tailwind
  - ↳ Test: `npm run dev` shows default page
- [ ] Write `backend/db/connection.py` — async Postgres connection via asyncpg
- [ ] Write `backend/db/models.py` — define tables (memories, facts, conversations)
- [ ] Run `alembic init` + write first migration
  - ↳ Test: `alembic upgrade head` creates tables in DB
- [ ] Confirm pgvector extension installs: `CREATE EXTENSION vector;`

---

## Phase 1 — Bare Agent Loop
**Goal:** You can type a message and get a response. No tools, no memory, no voice.
**Time:** 1 weekend

### Backend
- [ ] Write `backend/providers/base.py` — `BaseProvider` abstract class
- [ ] Write `backend/providers/gemini.py` — first working provider
  - ↳ Test: call it directly in a script, get a response back
- [ ] Write `backend/providers/__init__.py` — `get_provider()` factory
- [ ] Write `backend/agent/prompts.py` — base system prompt for Jarvis personality
- [ ] Write `backend/agent/loop.py` — bare agent loop (no tools, no memory yet)
  - Input: user message + conversation history
  - Output: assistant response string
- [ ] Write `backend/main.py` — FastAPI app with `POST /chat` endpoint
  - ↳ Test: `curl -X POST /chat -d '{"message": "hello"}'` returns response
- [ ] Add SSE streaming to `/chat` — yield tokens as they arrive
  - ↳ Test: response streams in terminal

### Frontend
- [ ] Build `frontend/lib/api.ts` — typed API client for backend
- [ ] Build `frontend/hooks/useChat.ts` — manages message state + API calls
- [ ] Build `frontend/components/Chat.tsx` — message list + input box
- [ ] Wire SSE streaming into chat UI — tokens appear in real time
- [ ] Build `frontend/app/page.tsx` — render Chat component
  - ↳ Test: full conversation works end to end in browser

---

## Phase 2 — Provider Abstraction
**Goal:** All 5 providers work. Swapping `LLM_PROVIDER` in `.env` just works.
**Time:** 3–5 days

- [ ] Write `backend/providers/claude.py` — Anthropic provider
  - ↳ Test: set `LLM_PROVIDER=claude`, chat works
- [ ] Write `backend/providers/openai.py` — OpenAI provider
  - ↳ Test: set `LLM_PROVIDER=openai`, chat works
- [ ] Write `backend/providers/groq.py` — Groq provider (OpenAI-compatible)
  - ↳ Test: set `LLM_PROVIDER=groq`, chat works
- [ ] Write `backend/providers/ollama.py` — local Ollama provider
  - ↳ Test: `ollama pull llama3.1`, set `LLM_PROVIDER=ollama`, chat works
- [ ] Add provider info endpoint `GET /provider` — returns current active model
- [ ] Show active model name in frontend UI (small badge, bottom corner)

---

## Phase 3 — Memory
**Goal:** Jarvis remembers things across conversations.
**Time:** 1 weekend

### Semantic Memory
- [ ] Pull `nomic-embed-text` via Ollama: `ollama pull nomic-embed-text`
- [ ] Write `backend/memory/semantic.py`
  - `store_memory(content, source)` — embed + insert into pgvector
  - `search_memories(query, top_k=5)` — cosine similarity search
  - ↳ Test: store 5 memories, search returns relevant ones
- [ ] Write conversation summarizer — summarize last N turns into a memory
- [ ] Wire into agent loop — after every 10 turns, summarize + store

### Explicit Facts
- [ ] Write `backend/memory/facts.py`
  - `set_fact(key, value)`
  - `get_fact(key)`
  - `get_all_facts()` → dict
- [ ] Write fact-extraction logic — detect when user states a personal fact
  - e.g. "my name is X", "I wake up at Y", "I work at Z"
- [ ] Wire facts + semantic memories into system prompt on every request
  - ↳ Test: tell Jarvis your name, start new conversation, it remembers

---

## Phase 4 — Voice
**Goal:** You can speak to Jarvis and hear it respond.
**Time:** 1 weekend

### STT — Whisper
- [ ] Install Whisper + ffmpeg
- [ ] Write `backend/voice/stt.py` — load model at startup, transcribe audio
- [ ] Add `POST /voice/transcribe` endpoint — accepts audio blob, returns text
  - ↳ Test: send a `.wav` file, get transcript back

### TTS
- [ ] Write `backend/voice/tts.py`
  - Try ElevenLabs first if key exists
  - Fall back to `pyttsx3` if no key
- [ ] Add `POST /voice/speak` endpoint — accepts text, streams audio back
- [ ] Add markdown stripper before TTS (remove `**`, code blocks, etc.)

### Frontend Voice UI
- [ ] Build `frontend/components/VoiceButton.tsx` — push-to-talk button
- [ ] Build `frontend/hooks/useVoice.ts`
  - Record audio via `MediaRecorder`
  - POST to `/voice/transcribe`
  - Auto-submit transcript to chat
- [ ] Build `frontend/components/AudioVisualizer.tsx` — waveform during recording/playback
- [ ] Wire TTS playback — after response, POST to `/voice/speak`, play audio
  - ↳ Test: speak a question, hear the answer

---

## Phase 5 — Core Tools
**Goal:** Jarvis can take real actions. This is where it becomes actually useful.
**Time:** 2–3 weeks

### 5A — System & Computer Tools
- [ ] Write `backend/tools/system.py`
  - `get_battery()` — battery level + charging status
  - `get_ram()` — used/total RAM
  - `get_os_info()` — OS name, version, uptime
  - `get_ip()` — local + public IP
  - `get_hostname()`
  - ↳ Uses: `psutil`, `socket`, `platform`
- [ ] Write `backend/tools/network.py`
  - `run_speedtest()` — download/upload speed via `speedtest-cli`
  - `scan_network()` — active devices on LAN via `nmap`
  - `dns_lookup(domain)` — forward DNS
  - `dns_reverse(ip)` — reverse DNS
- [ ] Write `backend/tools/screenshot.py`
  - `take_screenshot()` — saves to `/tmp/`, returns path
  - `open_camera()` — capture from webcam via `opencv`
- [ ] Register all tools in `backend/agent/tools.py`
  - ↳ Test: ask "what's my battery?" — correct answer

### 5B — File & Image Tools
- [ ] Write `backend/tools/files.py`
  - `list_directory(path)`
  - `read_file(path)`
  - `search_files(query, directory)` — find files by name/content
  - `organize_files(directory)` — sort files into subfolders by type
  - `delete_file(path)` — with confirmation flag
- [ ] Write `backend/tools/images.py`
  - `compress_image(path, quality)` — via `Pillow`
  - `convert_image(path, format)` — jpg/png/webp
  - `image_to_pdf(paths)` — via `img2pdf`
  - `upload_to_imgur(path)` — Imgur API (free, anonymous upload)
- [ ] Write `backend/tools/pdf.py`
  - `html_to_pdf(url)` — via `weasyprint`
  - `pdf_to_images(path)` — via `pdf2image`
  - `merge_pdfs(paths)` — via `pypdf`

### 5C — Weather & Location
- [ ] Write `backend/tools/weather.py`
  - `get_weather(location)` — current + 7-day forecast
  - Uses Open-Meteo API (free, no key needed)
  - ↳ Test: ask "what's the weather in Toronto?" — real forecast

### 5D — Sports
- [ ] Write `backend/tools/sports.py`
  - `get_standings(sport, league)` — team rankings
  - `get_fixtures(sport, team)` — upcoming matches
  - `get_player_stats(player, sport)`
  - Supports: basketball, cricket, soccer, tennis
  - Uses: API-Sports (free tier: 100 req/day) or ESPN public endpoints
  - ↳ Test: ask "when does [team] play next?" — correct fixture

### 5E — Health & Fitness
- [ ] Write `backend/tools/health.py`
  - `calculate_bmi(weight_kg, height_cm)`
  - `calculate_bmr(weight, height, age, gender)`
  - `calculate_calories(activity, duration)`
  - `get_nutrition(food_item)` — Open Food Facts API (free)
  - `get_fruit_info(fruit)` — Fruityvice API (free)
  - `get_workout(muscle_group, difficulty)` — wger API (free)

### 5F — Communication & Productivity
- [ ] Write `backend/tools/email.py`
  - `send_email(to, subject, body)` — Gmail API
  - `read_emails(count, filter)` — unread / from person / by subject
  - `search_emails(query)`
  - ↳ Requires: Google OAuth2 setup (see TOOLS.md)
- [ ] Write `backend/tools/calendar.py`
  - `get_events(days_ahead)` — upcoming events
  - `create_event(title, start, end, description)`
  - `find_free_slots(date)` — when are you free?
  - ↳ Requires: Google Calendar API OAuth2

---

## Phase 6 — Proactive Scheduler
**Goal:** Jarvis alerts you without you asking. Deadlines, weather, reminders.
**Time:** 3–5 days

- [ ] Install APScheduler: `pip install apscheduler`
- [ ] Write `backend/scheduler/jobs.py`
  - `check_deadlines()` — runs every morning, scans calendar for events in next 48h
  - `check_weather()` — morning briefing if rain/snow forecast
  - `send_reminder(message, time)` — one-time scheduled reminder
- [ ] Add scheduler startup to `backend/main.py` — starts with app
- [ ] Build notification system — POST to frontend via WebSocket or SSE push
- [ ] Build `frontend/components/Notification.tsx` — toast alerts for proactive messages
  - ↳ Test: create a calendar event for tomorrow, restart backend, get alerted

---

## Phase 7 — LLM-Native Features
**Goal:** All features the LLM handles natively — wired up cleanly with good prompts.
**Time:** 3–5 days

These need no external APIs — just good prompting and optionally a code execution tool.

- [ ] Games — verify these work well via conversation:
  - Blackjack, Hangman, Rock-Paper-Scissors, Tic-Tac-Toe
  - Guess the Number, Word Game, Wordle (LLM picks word + judges guesses)
  - Connect Four (LLM maintains board state in text)
  - Roulette (LLM simulates spin)
- [ ] Add `backend/tools/code_exec.py` — run Python snippets in subprocess sandbox
  - Used for: plotting, matrix math, equation solving, complex calculations
  - `execute_python(code)` → stdout output
- [ ] Verify calculations work: `calculate`, `factor`, `solve equations`, `plot`, `matrix`
- [ ] Verify generators work: `random number`, `random password`, `random list`
- [ ] Verify conversions work: all unit types (temp, currency via tool, length, speed, etc.)
- [ ] Write `backend/tools/qr.py` — `generate_qr(url)` → saves PNG, returns path
- [ ] Write `backend/tools/translate.py` — wraps LLM translation with language detection
- [ ] Add entertainment prompts to system prompt — activities, draw/watch/listen ideas, mood music

---

## Phase 8 — UI Polish
**Goal:** It looks like something you'd actually want to open every day.
**Time:** 1 weekend

- [ ] Design final chat UI — dark theme, clean typography, message bubbles
- [ ] Add sidebar — conversation history, active model badge, settings
- [ ] Polish audio visualizer — smooth waveform animation
- [ ] Add loading states — typing indicator while Jarvis thinks
- [ ] Add tool execution indicators — "Searching the web...", "Checking calendar..."
- [ ] Add settings panel — swap LLM provider from UI (writes to `.env`, restarts backend)
- [ ] Add onboarding flow — first run asks your name, timezone, preferences → stores as facts
- [ ] Mobile responsive — works on phone browser on local network

---

## Phase 9 — Hardening
**Goal:** It doesn't break when you look at it funny.
**Time:** 1 week

- [ ] Add retry logic to all provider calls — exponential backoff on rate limit
- [ ] Add tool error handling — every tool returns graceful error string, never crashes agent
- [ ] Add request timeout to all external API calls (10s default)
- [ ] Add conversation length management — summarize + trim when context gets too long
- [ ] Write basic test suite — one test per tool, one test per provider
- [ ] Add logging — structured logs for all agent loop steps, tool calls, errors
- [ ] Add `.env` validation on startup — fail loudly if required vars are missing
- [ ] Document all Google OAuth setup steps (email + calendar) in README

---

## Feature → Phase Reference

| Feature | Phase |
|---|---|
| Basic chat | 1 |
| Swap AI model | 2 |
| Memory / remembers you | 3 |
| Voice in/out | 4 |
| Weather | 5C |
| Sports updates | 5D |
| System info (battery, RAM, IP) | 5A |
| Screenshot / camera | 5A |
| File management | 5B |
| Image processing / PDF tools | 5B |
| Send emails | 5F |
| Calendar events | 5F |
| Health / BMI / nutrition / workout | 5E |
| Proactive deadline alerts | 6 |
| Morning briefing | 6 |
| Games | 7 |
| Calculations / equations / plotting | 7 |
| Unit conversions | 7 |
| Random generators | 7 |
| QR code generation | 7 |
| Translation | 7 |
| Entertainment suggestions | 7 |
| UI polish | 8 |
| Stability + error handling | 9 |

---

## Total Estimated Time

| Phase | Time |
|---|---|
| 0 — Setup | 2–4 hours |
| 1 — Agent loop | 1 weekend |
| 2 — Providers | 3–5 days |
| 3 — Memory | 1 weekend |
| 4 — Voice | 1 weekend |
| 5 — Core tools | 2–3 weeks |
| 6 — Scheduler | 3–5 days |
| 7 — LLM features | 3–5 days |
| 8 — UI polish | 1 weekend |
| 9 — Hardening | 1 week |
| **Total** | **~8–10 weeks part-time** |

Phase 1–4 alone gives you a working, voice-enabled AI assistant with memory.
Everything after that is adding capabilities on top of a solid foundation.
