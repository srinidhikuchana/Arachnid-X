"""
Thin wrapper around the OpenRouter API (OpenAI-compatible chat completions).
"""

import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# OpenRouter's free-model auto-router. It picks from whatever free models
# are currently available, so it won't break when individual :free models
# get rotated out (which happens often). If you want to pin an exact model
# instead, browse https://openrouter.ai/models?max_price=0 and swap the
# string below for something like "meta-llama/llama-3.3-70b-instruct:free".
DEFAULT_MODEL = "openrouter/free"


def get_ai_response(system_prompt: str, chat_history: list[dict], user_message: str,
                     model: str = DEFAULT_MODEL) -> str:
    """
    chat_history: list of {"role": "user"/"assistant", "content": str}
    Returns the assistant's reply as a string.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return ("⚠️ No OPENROUTER_API_KEY found. Add it to your .env file "
                "(see README for steps).")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.8,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"⚠️ Network/API error: {e}"
    except (KeyError, IndexError):
        return f"⚠️ Unexpected response format from OpenRouter: {resp.text[:300]}"
