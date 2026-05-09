"""
Deepgram Voice Agent settings — one place for every knob.

`voice_deepgram.py` handles the WebSocket bridging; *this* module owns the
`Settings` payload and the three provider blocks inside it (listen / think /
speak). If you want to change a model, voice, or sample rate, you change it
here and nowhere else.

The Voice Agent API contract is documented under `deepgram_docs_ref/`
(see `configure_the_voice_agent.md` and `llm_models.md`).
"""

from __future__ import annotations

from typing import Any

from . import FUNCTIONS, GREETING, PROMPT

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
# Matches what the browser already produces / plays back (see static/index.html).
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000

AUDIO_SETTINGS: dict[str, Any] = {
    "input": {
        "encoding": "linear16",
        "sample_rate": INPUT_SAMPLE_RATE,
    },
    "output": {
        "encoding": "linear16",
        "sample_rate": OUTPUT_SAMPLE_RATE,
        "container": "none",
    },
}

# ---------------------------------------------------------------------------
# Listen (speech-to-text)
# ---------------------------------------------------------------------------
# Deepgram's own model — fast, streaming, handles interruptions well.
LISTEN_PROVIDER: dict[str, Any] = {
    "type": "deepgram",
    "model": "nova-3",
}

# ---------------------------------------------------------------------------
# Think (LLM)
# ---------------------------------------------------------------------------
# Google Gemini 3.1 Flash Lite via Deepgram's managed endpoint — chosen for
# low time-to-first-tool-call, which is what the user perceives as slide-switch
# latency. `temperature` is kept low (0.3) because the persona is scripted and
# we want `change_slide` to fire reliably on nav phrases rather than the model
# getting creative.
THINK_PROVIDER: dict[str, Any] = {
    "type": "google",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.3,
}

# ---------------------------------------------------------------------------
# Speak (text-to-speech)
# ---------------------------------------------------------------------------
# Cartesia Sonic-2, "Brooke" — warm authoritative female.
SPEAK_PROVIDER: dict[str, Any] = {
    "type": "cartesia",
    "model_id": "sonic-2",
    "voice": {
        "mode": "id",
        "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab",
    },
    "speed": "normal",
}

# ---------------------------------------------------------------------------
# Top-level assembly
# ---------------------------------------------------------------------------
LANGUAGE = "en"


def settings_payload() -> dict[str, Any]:
    """Build the `Settings` frame sent to Deepgram at session start."""
    return {
        "type": "Settings",
        "audio": AUDIO_SETTINGS,
        "agent": {
            "language": LANGUAGE,
            "listen": {"provider": LISTEN_PROVIDER},
            "think": {
                "provider": THINK_PROVIDER,
                "prompt": PROMPT,
                "functions": list(FUNCTIONS),
            },
            "speak": {"provider": SPEAK_PROVIDER},
            "greeting": GREETING,
        },
    }


__all__ = [
    "AUDIO_SETTINGS",
    "INPUT_SAMPLE_RATE",
    "LANGUAGE",
    "LISTEN_PROVIDER",
    "OUTPUT_SAMPLE_RATE",
    "SPEAK_PROVIDER",
    "THINK_PROVIDER",
    "settings_payload",
]
