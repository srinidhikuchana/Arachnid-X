import re
import hashlib
import streamlit as st
from dotenv import load_dotenv

from config.prompts import PERSONAS
from core.llm import get_ai_response
from core.stt import transcribe_audio
from core.tts import speak
from database.memory import get_user_name, set_user_name

load_dotenv()

st.set_page_config(page_title="Arachnid-X", page_icon="🛡️", layout="centered")

# ---------- Session state setup ----------
if "mode" not in st.session_state:
    st.session_state.mode = "aegis"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"aegis": [], "noctis": []}
if "user_name" not in st.session_state:
    st.session_state.user_name = get_user_name()
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = ""
if "pending_tts" not in st.session_state:
    st.session_state.pending_tts = None

persona = PERSONAS[st.session_state.mode]

# ---------- Simple name detection ----------
NAME_PATTERN = re.compile(r"\bmy name is (\w+)\b|\bi'?m (\w+)\b|\bi am (\w+)\b", re.IGNORECASE)


def maybe_capture_name(text: str):
    match = NAME_PATTERN.search(text)
    if match:
        name = next(g for g in match.groups() if g)
        st.session_state.user_name = name
        set_user_name(name)


def handle_user_message(user_input: str):
    """Send a message (typed or transcribed) to the current persona and store the reply."""
    history = st.session_state.chat_history[st.session_state.mode]
    maybe_capture_name(user_input)
    history.append({"role": "user", "content": user_input})

    system_prompt = persona["system_prompt"]
    if st.session_state.user_name:
        system_prompt += (
            f"\n\nThe user's name is {st.session_state.user_name}. "
            "Use it naturally, not every message."
        )

    with st.spinner(f"{persona['display_name']} is thinking..."):
        reply = get_ai_response(system_prompt, history[:-1], user_input)

    history.append({"role": "assistant", "content": reply})
    st.session_state.pending_tts = reply


# ---------- Theming: original web pattern (radial lines + concentric arcs) ----------
# Hand-built geometric shapes, not Marvel/Spider-Man artwork. Color/opacity
# adapt so it reads clearly on both light (Aegis) and dark (Noctis) themes.
_web_stroke = persona['accent_color'] if persona["theme"] == "dark" else persona['primary_color']
_web_opacity = "0.35" if persona["theme"] == "dark" else "0.14"

_WEB_SVG = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>
  <g stroke='{_web_stroke}' stroke-width='1' fill='none' opacity='{_web_opacity}'>
    <line x1='150' y1='150' x2='150' y2='0' />
    <line x1='150' y1='150' x2='150' y2='300' />
    <line x1='150' y1='150' x2='0' y2='150' />
    <line x1='150' y1='150' x2='300' y2='150' />
    <line x1='150' y1='150' x2='45' y2='45' />
    <line x1='150' y1='150' x2='255' y2='45' />
    <line x1='150' y1='150' x2='45' y2='255' />
    <line x1='150' y1='150' x2='255' y2='255' />
    <circle cx='150' cy='150' r='40' />
    <circle cx='150' cy='150' r='90' />
    <circle cx='150' cy='150' r='140' />
  </g>
</svg>
"""
_WEB_SVG_ENCODED = _WEB_SVG.replace("\n", "").replace("#", "%23")
_web_bg_css = f'url("data:image/svg+xml,{_WEB_SVG_ENCODED}")'

st.markdown(f"""
<style>
    html, body {{
        background-color: {persona['bg_color']} !important;
    }}

    /* These sit on top of .stApp — make them transparent so the web
       pattern painted on .stApp shows through everywhere, including
       behind the chat messages, not just the outer margins */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stHeader"],
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {{
        background-color: transparent !important;
    }}

    /* The web pattern lives on .stApp itself, set together so nothing else
       can silently override just one of the two properties */
    .stApp {{
        background-color: {persona['bg_color']} !important;
        background-image: {_web_bg_css} !important;
        background-repeat: repeat !important;
    }}

    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    /* Base text color for the whole app */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {{
        color: {persona['text_color']};
    }}

    .persona-header {{
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid {persona['accent_color']};
        margin-bottom: 1rem;
    }}
    .persona-header h1 {{
        color: {persona['accent_color']};
        margin-bottom: 0;
    }}
    .persona-header p {{
        color: {persona['muted_color']};
        margin-top: 0;
    }}

    /* Chat message bubbles */
    [data-testid="stChatMessage"] {{
        background-color: {persona['surface_color']};
        border-radius: 12px;
        border: 1px solid {persona['accent_color']}33;
        color: {persona['text_color']};
    }}
    [data-testid="stChatMessage"] p {{
        color: {persona['text_color']} !important;
    }}

    /* --- Input row: text box styled to match theme --- */
    .stTextInput > div > div > input {{
        background-color: {persona['surface_color']} !important;
        color: {persona['text_color']} !important;
        border: 1.5px solid {persona['accent_color']} !important;
        border-radius: 10px !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: {persona['muted_color']} !important;
    }}

    /* --- Voice input (mic) --- */
    div[data-testid="stAudioInput"] {{
        background: transparent !important;
        border: none !important;
    }}
    div[data-testid="stAudioInput"] > div {{
        background-color: {persona['surface_color']} !important;
        border: 1.5px solid {persona['accent_color']} !important;
        border-radius: 10px !important;
    }}
    /* Catch every inner element (waveform/timer box included) so nothing
       renders with Streamlit's default white background */
    div[data-testid="stAudioInput"] * {{
        background-color: {persona['surface_color']} !important;
        color: {persona['text_color']} !important;
        border-color: {persona['accent_color']} !important;
    }}
    div[data-testid="stAudioInput"] svg {{
        fill: {persona['accent_color']} !important;
    }}

    /* Buttons (mode switch + send) */
    .stButton button {{
        border: 1.5px solid {persona['accent_color']} !important;
        background-color: {persona['surface_color']} !important;
        color: {persona['text_color']} !important;
    }}
    .stButton button p {{
        color: {persona['text_color']} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="persona-header">
    <h1>🕸️ ARACHNID-X</h1>
    <p>TWO MINDS. ONE MISSION.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Mode switch ----------
col1, col2 = st.columns(2)
with col1:
    if st.button("🕸️ AEGIS", use_container_width=True,
                 type="primary" if st.session_state.mode == "aegis" else "secondary"):
        st.session_state.mode = "aegis"
        st.rerun()
with col2:
    if st.button("🌑 NOCTIS", use_container_width=True,
                 type="primary" if st.session_state.mode == "noctis" else "secondary"):
        st.session_state.mode = "noctis"
        st.rerun()

st.caption(f"**{persona['display_name']}** — {persona['subtitle']}")

# ---------- Chat display ----------
history = st.session_state.chat_history[st.session_state.mode]

if not history:
    st.chat_message("assistant").write(persona["greeting"])

for msg in history:
    st.chat_message(msg["role"]).write(msg["content"])

# ---------- Input row: mic (left) + text box + send ----------
col_mic, col_text, col_send = st.columns([1.2, 4, 1])

with col_mic:
    audio_value = st.audio_input(f"Speak to {persona['display_name']}", label_visibility="collapsed")
with col_text:
    user_text = st.text_input(f"Talk to {persona['display_name']}...",
                               placeholder=f"Talk to {persona['display_name']}...",
                               label_visibility="collapsed", key="user_text_input")
with col_send:
    send_clicked = st.button("Send", use_container_width=True)

if audio_value is not None:
    audio_bytes = audio_value.read()
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        with st.spinner("Transcribing..."):
            transcribed = transcribe_audio(audio_bytes)

        if transcribed:
            handle_user_message(transcribed)
            st.rerun()
        else:
            st.warning("Couldn't transcribe that — check GROQ_API_KEY in your .env, or try again.")

if send_clicked and user_text.strip():
    handle_user_message(user_text.strip())
    st.rerun()

# ---------- Speak the latest reply ----------
if st.session_state.pending_tts:
    speak(st.session_state.pending_tts)
    st.session_state.pending_tts = None

# ---------- Footer ----------
st.markdown(f"""
<div style="text-align:center; margin-top:2rem; padding-top:1rem;
            border-top:1px solid {persona['accent_color']}33;">
    <span style="font-size:0.8rem; color:{persona['muted_color']};">
        Arachnid-X is an original dual personality assistant (Aegis &amp; Noctis),
        not affiliated with Marvel or any existing franchise.
    </span>
</div>
""", unsafe_allow_html=True)
