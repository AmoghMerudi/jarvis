# VOICE.md — Voice System Reference

## Overview

Voice in Jarvis works in two directions:
- **STT (Speech-to-Text):** User speaks → Whisper transcribes → text enters agent loop
- **TTS (Text-to-Speech):** Agent responds → ElevenLabs synthesizes → audio plays

Both are optional per-request. The chat interface supports text-only, voice-only, or mixed.

---

## STT — Whisper (Local)

### Why Whisper
Runs 100% locally. No API calls, no usage limits, no audio leaving your machine. Accurate enough for casual speech.

### Setup
```bash
pip install openai-whisper
# Also needs ffmpeg
brew install ffmpeg  # macOS
```

### Model Selection
Set via `WHISPER_MODEL` env var.

| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| `tiny` | Fastest | Lower | ~1GB |
| `base` | Fast | Good | ~1GB |
| `small` | Medium | Better | ~2GB |
| `medium` | Slow | Best for local | ~5GB |

**Recommended:** `base` to start. Upgrade to `small` if accuracy is lacking.

### FastAPI Endpoint
```
POST /voice/transcribe
Content-Type: multipart/form-data
Body: audio file (webm, wav, mp3, ogg)

Response: { "text": "transcribed text here" }
```

### Implementation Notes
- Load Whisper model once at startup — not per-request (it's slow to load)
- Convert audio to 16kHz mono WAV before passing to Whisper (ffmpeg handles this)
- Transcription of a 5-second clip takes ~0.5-2s on M-series Mac with `base` model

---

## TTS — ElevenLabs

### Why ElevenLabs
Best-in-class voice quality. Free tier: 10,000 characters/month — plenty for personal use.

### Voice Selection
Pick a voice ID from ElevenLabs dashboard. Store it in env:
```
ELEVENLABS_VOICE_ID=your_voice_id_here
```

Good starting voices for an assistant feel: `Adam`, `Antoni`, `Josh`. Try a few.

### FastAPI Endpoint
```
POST /voice/speak
Content-Type: application/json
Body: { "text": "response text to synthesize" }

Response: audio/mpeg stream
```

### Streaming Audio
Stream the audio back rather than waiting for full generation:
```python
# ElevenLabs supports streaming
# Stream chunks back to frontend as they arrive
# Frontend plays using Web Audio API
```

### Implementation Notes
- Strip markdown before sending to ElevenLabs (`**bold**` → `bold`)
- Strip code blocks entirely — don't read them aloud
- Max ~500 chars per TTS call for snappy response. Split longer responses.
- Cache common short phrases locally (optional optimisation later)

---

## Frontend Voice UI

### Recording Flow
1. User presses and holds voice button (or click-to-toggle)
2. Browser requests microphone permission
3. `MediaRecorder` captures audio as `webm` blob
4. On release → POST blob to `/voice/transcribe`
5. On success → text populates input field AND auto-submits

### Playback Flow
1. Response arrives from agent
2. POST response text to `/voice/speak`
3. Receive audio stream
4. Play via `<audio>` element or Web Audio API

### Audio Visualizer
Show a waveform animation while:
- Recording (microphone input)
- Playing back (TTS output)

Use `AnalyserNode` from Web Audio API. Keep it minimal — this is a utility tool, not a music player.

### Browser Permissions
- Microphone: requested on first voice button press
- Autoplay: audio playback may be blocked by browser on first interaction — handle gracefully

---

## Silence Detection (Optional Enhancement)

Instead of push-to-talk, auto-stop recording after N seconds of silence:

```typescript
// Use AudioContext + AnalyserNode
// If RMS energy < threshold for > 1.5s → stop recording
// Threshold: ~0.01 works for quiet rooms
```

Implement only after basic PTT is working.

---

## Fallback Behaviour

If ElevenLabs is unavailable (rate limit, no key):
- Fall back to browser `SpeechSynthesis` API
- Lower quality but zero dependencies

If Whisper fails:
- Show error in UI
- Fall back to text input — voice failure should never block chat
