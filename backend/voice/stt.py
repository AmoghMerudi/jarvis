import os
import tempfile
from pathlib import Path

import whisper

_model: whisper.Whisper | None = None


def _get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        model_name = os.environ.get("WHISPER_MODEL", "base")
        _model = whisper.load_model(model_name)
    return _model


def transcribe(audio_bytes: bytes, extension: str = "webm") -> str:
    model = _get_model()
    with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path)
        return result["text"].strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
