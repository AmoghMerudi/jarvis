# TOOLS.md — Complete Tool Reference

## Overview

Tools are how Jarvis takes real actions. Each tool is a Python async function registered
in `backend/agent/tools.py`. The LLM decides when and how to call them.

Two categories:
- **Real tools** — need implementation, call APIs or system libs
- **LLM-native** — the model handles these directly, no tool needed

---

## Tool Registration Pattern

```python
TOOL_DEFINITION = {
    "name": "tool_name",
    "description": "Clear description. When to use it. What it returns.",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "What this is"}
        },
        "required": ["param"]
    }
}

async def execute(input: dict) -> str:
    # Always return a plain string
    # On error: return "Error: [description]" — never raise
    return "result"
```

Register in `backend/agent/tools.py`:
```python
TOOLS = [weather, sports, system_info, ...]  # list of (definition, execute) pairs
```

---

## LLM-Native Features (No Tool Needed)

The LLM handles these directly. Don't build tools for them.

| Feature | Notes |
|---|---|
| **Games** | Blackjack, Hangman, RPS, Tic-Tac-Toe, Connect Four, Wordle, Roulette, Guess the Number, Word Game |
| **Jokes & Facts** | Dad jokes, Chuck Norris jokes, daily facts, cat facts |
| **Unit Conversions** | Temperature, length, mass, speed, time, binary, hex, string |
| **Calculations** | Basic math, BMI, BMR, calories |
| **Random generators** | Random number, password, list |
| **Translation** | All languages |
| **Entertainment suggestions** | Activity ideas, drawing prompts, watch/listen recs, mood music |
| **Cocktail & food recipes** | LLM knowledge |
| **Workout programs** | LLM knowledge |

---

## Real Tools — By Module

### `backend/tools/weather.py`
Free. No key. Uses Open-Meteo.

| Tool | Input | Output |
|---|---|---|
| `get_weather` | `location: str` | Current conditions + 7-day forecast |
| `get_weather_alert` | `location: str` | Rain/snow/storm alerts only |

---

### `backend/tools/sports.py`
Free tier. API-Sports: 100 req/day free.

| Tool | Input | Output |
|---|---|---|
| `get_standings` | `sport, league` | Team rankings table |
| `get_fixtures` | `sport, team` | Upcoming matches + times |
| `get_live_scores` | `sport, league` | Live match scores |
| `get_player_stats` | `player_name, sport` | Stats for current season |

Supported sports: `basketball`, `cricket`, `soccer`, `tennis`

---

### `backend/tools/system.py`
Free. Local. Uses `psutil` + `platform` + `socket`.

| Tool | Input | Output |
|---|---|---|
| `get_battery` | none | Battery %, charging status |
| `get_ram` | none | Used / total RAM |
| `get_os_info` | none | OS, version, uptime, hostname |
| `get_ip` | none | Local IP + public IP |
| `get_system_info` | none | Full system snapshot |
| `get_cpu_usage` | none | CPU % per core |
| `get_disk_usage` | `path?` | Disk used/free |

---

### `backend/tools/network.py`
Free. Local. Uses `speedtest-cli` + `nmap`.

| Tool | Input | Output |
|---|---|---|
| `run_speedtest` | none | Download/upload Mbps, ping |
| `scan_network` | none | Active devices on LAN |
| `dns_lookup` | `domain: str` | IP addresses for domain |
| `dns_reverse` | `ip: str` | Hostname for IP |

---

### `backend/tools/files.py`
Free. Local filesystem.

| Tool | Input | Output |
|---|---|---|
| `list_directory` | `path: str` | Directory contents |
| `read_file` | `path: str` | File contents (truncated > 8000 chars) |
| `search_files` | `query, directory` | Files matching name/content |
| `organize_files` | `directory: str` | Sorts files into type subfolders |
| `move_file` | `src, dest` | Moves file |
| `delete_file` | `path, confirmed` | Requires `confirmed=true` |

Security: Only allow within user home dir. Reject paths with `..`.

---

### `backend/tools/images.py`
Free. Local. Uses `Pillow` + `img2pdf`.

| Tool | Input | Output |
|---|---|---|
| `compress_image` | `path, quality (1-100)` | New path |
| `convert_image` | `path, format` | New path (jpg/png/webp) |
| `resize_image` | `path, width, height` | New path |
| `image_to_pdf` | `paths: list[str]` | PDF path |
| `upload_to_imgur` | `path: str` | Public Imgur URL |

---

### `backend/tools/pdf.py`
Free. Local. Uses `weasyprint` + `pdf2image` + `pypdf`.

| Tool | Input | Output |
|---|---|---|
| `html_to_pdf` | `url: str` | PDF path |
| `pdf_to_images` | `path: str` | List of image paths |
| `merge_pdfs` | `paths: list[str]` | Merged PDF path |
| `split_pdf` | `path, pages` | Split PDF paths |

---

### `backend/tools/screenshot.py`
Free. Local. Uses `pyautogui` + `opencv`.

| Tool | Input | Output |
|---|---|---|
| `take_screenshot` | `region?` | Screenshot path |
| `open_camera` | `duration?` | Webcam photo path |

---

### `backend/tools/health.py`
Free. Mix of local math + Open Food Facts + Fruityvice + wger APIs.

| Tool | Input | Output |
|---|---|---|
| `calculate_bmi` | `weight_kg, height_cm` | BMI value + category |
| `calculate_bmr` | `weight, height, age, gender` | Basal metabolic rate |
| `calculate_calories` | `activity, duration_min, weight_kg` | Calories burned |
| `get_nutrition` | `food_item: str` | Macros + calories |
| `get_fruit_info` | `fruit: str` | Nutrition facts |
| `get_workout_plan` | `muscle_group, difficulty` | Exercise list |

---

### `backend/tools/email.py`
Free. Requires Google OAuth2.

| Tool | Input | Output |
|---|---|---|
| `send_email` | `to, subject, body` | Confirmation |
| `read_emails` | `count, filter?` | Formatted email list |
| `search_emails` | `query: str` | Matching emails |
| `get_unread_count` | none | Unread count |

⚠️ Agent loop must show draft to user and wait for explicit "yes" before sending.

---

### `backend/tools/calendar.py`
Free. Requires Google OAuth2.

| Tool | Input | Output |
|---|---|---|
| `get_events` | `days_ahead: int` | Upcoming events |
| `create_event` | `title, start, end, description?` | Confirmation |
| `delete_event` | `event_id, confirmed` | Confirmation |
| `find_free_slots` | `date: str` | Open time windows |
| `get_deadlines` | `days_ahead: int` | Deadline events |

---

### `backend/tools/qr.py`
Free. Local. Uses `qrcode[pil]`.

| Tool | Input | Output |
|---|---|---|
| `generate_qr` | `url: str, filename?` | Path to saved QR PNG |

---

### `backend/tools/code_exec.py`
Free. Local. Sandboxed subprocess.

Used for: plotting, equations, matrix math, complex calculations.

| Tool | Input | Output |
|---|---|---|
| `execute_python` | `code: str` | stdout (10s timeout) |

Allowed imports: `math`, `numpy`, `matplotlib`, `sympy`
Blocked: `os`, `sys`, `subprocess`, `open()`, network

---

## Tool Output Guidelines

- Always return plain readable text
- Keep under 2000 chars — summarize if longer
- On error: `"Error: [description]"` — never raise out of tools
- For file ops: return the output path
- For confirmations: `"Done: [what happened]"`

---

## Adding a New Tool

1. Create `backend/tools/your_tool.py`
2. Define `TOOL_DEFINITION` + `async def execute(input: dict) -> str`
3. Register in `backend/agent/tools.py`
4. Test in isolation before wiring to agent
5. Add entry to this file
