"""Feline.ai voice-agent content: greeting, system prompt, and tool schemas."""

from __future__ import annotations

import json
from pathlib import Path

_DIR = Path(__file__).parent
_FUNCTIONS_DIR = _DIR / "functions"

GREETING: str = (_DIR / "greeting.md").read_text(encoding="utf-8").strip()
"""Spoken opener delivered as soon as the voice session starts."""

PROMPT: str = (_DIR / "prompt.md").read_text(encoding="utf-8").strip()
"""Full system prompt for the Feline.ai Founder-Visionary persona."""

FUNCTIONS: list[dict] = [
    json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(_FUNCTIONS_DIR.glob("*.json"))
]
"""Tool/function schemas exposed to the voice agent."""

__all__ = ["GREETING", "PROMPT", "FUNCTIONS"]
