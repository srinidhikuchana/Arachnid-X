"""
Speech-to-text using Groq's hosted Whisper model.
Mirrors the approach used in the user's Klyra project.
"""

import os
import tempfile
from groq import Groq


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe raw WAV bytes to text. Returns '' if no GROQ_API_KEY or on failure."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return ""

    client = Groq(api_key=api_key)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=("recording.wav", f, "audio/wav"),
                model="whisper-large-v3-turbo",
                prompt="User is talking to an AI assistant.",
            )
        return result.text.strip()
    except Exception:
        return ""
    finally:
        os.unlink(tmp_path)
