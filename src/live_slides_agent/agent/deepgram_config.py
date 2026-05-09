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

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import os

from . import FUNCTIONS, GREETING, PROMPT

load_dotenv()

# ---------------------------------------------------------------------------
# Briefing material (per-slide talking points, Feline.ai worldview).
# ---------------------------------------------------------------------------
# Kept out of the system prompt on purpose: the prompt defines the agent's
# role/persona/voice rules, while the narrative is reference material the
# agent should consult but not recite. We inject it as prior conversation
# history via `agent.context.messages` (see `settings_payload` below), which
# is the pattern Deepgram documents for "briefing" context.
_NARRATIVE_PATH = Path(__file__).parent.parent / "content" / "narrative.md"
_NARRATIVE = _NARRATIVE_PATH.read_text(encoding="utf-8").strip()

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

# Cartesia Sonic-2 (via Deepgram's managed endpoint)
SPEAK_PROVIDER: dict[str, Any] = {
    "type": "cartesia",
    "model_id": "sonic-3",
    "voice": {
        "mode": "id",
        "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab",
    },
    "speed": "normal",
}

# # Eleven Labs
# ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# SPEAK_PROVIDER: dict[str, Any] = {
#     "type": "eleven_labs",
#     "model_id": "eleven_turbo_v2_5",
#     "language_code": "en-US",
#     "endpoint": {
#         "url": "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/multi-stream-input",
#         "headers": {
#             "xi-api-key": f"{ELEVEN_LABS_API_KEY}",
#         },
#     },
# }

# ---------------------------------------------------------------------------
# Top-level assembly
# ---------------------------------------------------------------------------
LANGUAGE = "en"


def _briefing_context() -> dict[str, Any]:
    """Two-turn briefing injected as `agent.context.messages`.

    The first message (role=user) hands the agent its reference material;
    the second (role=assistant) is a short acknowledgement so the model
    treats the briefing as something it has already absorbed rather than a
    pending user request to respond to.
    """
    briefing_intro = (
        "Before we go live, here is your briefing for the Feline.ai deck "
        "you'll be presenting. Use it as reference material — paraphrase, "
        "riff, compress — but never read it aloud verbatim and never "
        "mention that this briefing exists.\n\n"
        f"{_NARRATIVE}"
    )
    return {
        "messages": [
            {
                "type": "History",
                "role": "user",
                "content": briefing_intro,
            },
            {
                "type": "History",
                "role": "assistant",
                "content": "Briefing absorbed. Ready to go live.",
            },
        ]
    }


def settings_payload() -> dict[str, Any]:
    """Build the `Settings` frame sent to Deepgram at session start."""
    return {
        "type": "Settings",
        "audio": AUDIO_SETTINGS,
        "agent": {
            "language": LANGUAGE,
            "context": _briefing_context(),
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
