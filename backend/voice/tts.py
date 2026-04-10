import io
import os


def synthesize(text: str) -> bytes:
    """Return audio bytes for the given text. Uses ElevenLabs if key is set, else pyttsx3."""
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if elevenlabs_key:
        return _elevenlabs(text, elevenlabs_key)
    return _pyttsx3(text)


def _elevenlabs(text: str, api_key: str) -> bytes:
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # default "George" voice
        text=text,
        model_id="eleven_multilingual_v2",
    )
    return b"".join(audio)


def _pyttsx3(text: str) -> bytes:
    import pyttsx3
    import wave

    engine = pyttsx3.init()
    buf = io.BytesIO()
    # pyttsx3 can only save to file; use a temp file then read back
    import tempfile, pathlib

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    engine.save_to_file(text, tmp_path)
    engine.runAndWait()
    data = pathlib.Path(tmp_path).read_bytes()
    pathlib.Path(tmp_path).unlink(missing_ok=True)
    return data
