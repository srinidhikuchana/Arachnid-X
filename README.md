# WebWarden AI

Dual-personality AI companion — **Aegis** (optimistic guardian) and **Noctis**
(dark protector) : two original characters, no Marvel IP. Built with
Streamlit and OpenRouter.

## 1. Get your API keys

**OpenRouter** (for chat replies):
1. Go to https://openrouter.ai and sign up (free).
2. Go to **Keys** → **Create Key**.
3. Copy the key (starts with `sk-or-...`).

**Groq** (for voice transcription, free tier available):
1. Go to https://console.groq.com and sign up (free).
2. Go to **API Keys** → **Create API Key**.
3. Copy the key (starts with `gsk_...`).

OpenRouter's `openrouter/free` router gives access to free models, so you don't need to pay anything to run this.

## 2. Local setup

```bash
# 1. Move into the project folder
cd webwarden-ai

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API keys
cp .env.example .env
# open .env and paste your real OpenRouter and Groq keys in place of the placeholders
```

Your `.env` should look like:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

## 3. Run the app

```bash
streamlit run app.py
```

This opens the app in your browser at `http://localhost:8501`.

## 4. Try it out

- Click **AEGIS** or **NOCTIS** to switch personas, notice the whole UI
  theme changes, and so does the way the AI responds.
- Type `My name is <yourname>` and it'll remember it (stored locally in
  `database/webwarden.db`) and use it later, even after you restart the app.
- Try the same question in both modes to see the personality difference:
  - "I'm stressed about my exam."
  - "What are you doing?"

## 5. Voice input & output

- Click the mic widget above the text box to record a question, it gets
  transcribed via Groq Whisper and sent to the current persona automatically.
- Every reply is also spoken aloud via gTTS (needs an internet connection;
  no extra key required beyond what's already in `.env`).
- If transcription fails, double check `GROQ_API_KEY` is set correctly.

## 7. Project structure

```
webwarden-ai/
├── app.py                 # Streamlit UI and main app loop
├── config/
│   └── prompts.py         # Persona definitions & system prompts
├── core/
│   ├── llm.py              # OpenRouter API wrapper
│   ├── stt.py               # Voice input: Groq Whisper transcription
│   └── tts.py               # Voice output: gTTS autoplay
├── database/
│   └── memory.py           # SQLite-backed persistent memory (user's name)
├── requirements.txt
├── .env.example
└── README.md
```

## 8. Swapping the model

Default model is `openrouter/free` (OpenRouter's auto-router for free models, it
adapts automatically as individual `:free` models rotate in and out). To pin
an exact model instead, edit `DEFAULT_MODEL` in `core/llm.py`. Browse options at
https://openrouter.ai/models, filter by `:free` if you want to stay on
the free tier.

## 7. Next steps (V2 ideas, not built yet)

- Voice input/output (SpeechRecognition + gTTS)
- Persistent chat history (not just the current name) per persona
- Deploy to Streamlit Community Cloud or a Docker container on your VPS
- A "Help Mode" tuned specifically for giving practical advice on real
  problems (bullying, stress, conflict) with a stronger safety layer

## 8. Deploying (optional, quick option)

Easiest free option: [Streamlit Community Cloud](https://streamlit.io/cloud).
Push this repo to GitHub, connect it on share.streamlit.io, and add
`OPENROUTER_API_KEY` under **App settings → Secrets** as:

```toml
OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
```

No server management needed for a demo/portfolio deployment.
