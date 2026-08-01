"""
Text-to-speech using edge-tts (Microsoft's neural voices), autoplayed via
an invisible <audio> tag. Switched from gTTS because gTTS only offers one
generic voice with no gender choice — edge-tts lets us pick a real male
voice for free.
"""

import base64
import asyncio
import streamlit as st
import edge_tts

# en-US-GuyNeural: Microsoft's standard US-English male neural voice.
# Browse more options with: edge-tts --list-voices
VOICE = "en-US-GuyNeural"


async def _generate(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes


def speak(text: str, voice: str = VOICE) -> None:
    """Generate speech for `text` and autoplay it in the browser."""
    if not text:
        return
    try:
        audio_bytes = asyncio.run(_generate(text, voice))
    except Exception:
        return
    if not audio_bytes:
        return

    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f'<audio autoplay style="display:none;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        f'</audio>',
        unsafe_allow_html=True,
    )
