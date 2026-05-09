"""
Bridge between the browser WebSocket and Deepgram's Voice Agent API.

Responsibilities:
- Open a WS to `wss://agent.deepgram.com/v1/agent/converse` with our API key.
- Send a `Settings` frame configured from our `agent/` module (prompt, greeting, tools).
- Forward raw PCM16 audio in both directions.
- Translate Deepgram's JSON events into the small contract our frontend already speaks:
    * `FunctionCallRequest` → `{type: "tool_call", name, arguments}` (and ack back to Deepgram)
    * `ConversationText`    → `{type: "transcript", speaker, text}`
  Everything else is logged and dropped.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

import websockets
from fastapi import WebSocket, WebSocketDisconnect

from .agent import FUNCTIONS, GREETING, PROMPT

logger = logging.getLogger(__name__)

DEEPGRAM_AGENT_URL = "wss://agent.deepgram.com/v1/agent/converse"

# Matches what the browser already produces / plays back (see static/index.html).
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000

# Same cap as the local-agent path.
MAX_WS_MESSAGE_BYTES = 64 * 1024 * 1024


# Cartesia Sonic-2, "Brooke" — warm authoritative female. Override with
# DEEPGRAM_SPEAK_PROVIDER_JSON if you want to try another voice without code changes.
DEFAULT_SPEAK_PROVIDER: dict[str, Any] = {
    "type": "cartesia",
    "model_id": "sonic-2",
    "voice": {"mode": "id", "id": "a167e0f3-df7e-4d52-a9c3-f949145efdab"},
    "speed": "normal",
}


def _speak_provider() -> dict[str, Any]:
    override = os.environ.get("DEEPGRAM_SPEAK_PROVIDER_JSON")
    if override:
        try:
            return json.loads(override)
        except json.JSONDecodeError:
            logger.warning(
                "DEEPGRAM_SPEAK_PROVIDER_JSON is not valid JSON; using default"
            )
    return DEFAULT_SPEAK_PROVIDER


def _functions_payload() -> list[dict[str, Any]]:
    # Functions without an `endpoint` are executed client-side by Deepgram's
    # contract — which is exactly what we want (we handle them in this bridge /
    # the browser). So: just pass them through untouched.
    return list(FUNCTIONS)


def _settings_payload() -> dict[str, Any]:
    return {
        "type": "Settings",
        "audio": {
            "input": {"encoding": "linear16", "sample_rate": INPUT_SAMPLE_RATE},
            "output": {
                "encoding": "linear16",
                "sample_rate": OUTPUT_SAMPLE_RATE,
                "container": "none",
            },
        },
        "agent": {
            "language": "en",
            "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
            "think": {
                "provider": {"type": "open_ai", "model": "gpt-4o-mini"},
                "prompt": PROMPT,
                "functions": _functions_payload(),
            },
            "speak": {"provider": _speak_provider()},
            "greeting": GREETING,
        },
    }


async def bridge_deepgram(browser: WebSocket) -> None:
    """Proxy one browser session through the Deepgram Voice Agent API."""
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        logger.warning("DEEPGRAM_API_KEY not set; refusing deepgram session")
        await browser.close(code=1011, reason="DEEPGRAM_API_KEY missing")
        return

    try:
        dg = await websockets.connect(
            DEEPGRAM_AGENT_URL,
            additional_headers={"Authorization": f"Token {api_key}"},
            max_size=MAX_WS_MESSAGE_BYTES,
        )
    except (OSError, websockets.WebSocketException) as exc:
        logger.warning("Deepgram upstream unreachable: %s", exc)
        await browser.close(code=1011, reason="deepgram unavailable")
        return

    try:
        await dg.send(json.dumps(_settings_payload()))
        done, pending = await asyncio.wait(
            {
                asyncio.create_task(_browser_to_dg(browser, dg)),
                asyncio.create_task(_dg_to_browser(browser, dg)),
            },
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        for task in done:
            if (exc := task.exception()) is not None:
                logger.warning("deepgram bridge task ended with %s", exc)
    finally:
        await dg.close()


async def _browser_to_dg(
    browser: WebSocket, dg: websockets.WebSocketClientProtocol
) -> None:
    try:
        while True:
            msg = await browser.receive()
            if msg["type"] == "websocket.disconnect":
                return
            if (data := msg.get("bytes")) is not None:
                await dg.send(data)
            elif (text := msg.get("text")) is not None:
                await dg.send(text)
    except WebSocketDisconnect:
        return
    except websockets.WebSocketException:
        return


async def _dg_to_browser(
    browser: WebSocket, dg: websockets.WebSocketClientProtocol
) -> None:
    try:
        async for msg in dg:
            if isinstance(msg, (bytes, bytearray)):
                # TTS audio — forward straight through.
                await browser.send_bytes(bytes(msg))
                continue

            # Text frame: log + translate the few events the frontend cares about.
            try:
                event = json.loads(msg)
            except json.JSONDecodeError:
                continue

            etype = event.get("type")
            t = time.monotonic()
            if etype == "FunctionCallRequest":
                logger.info("[lat] t=%.3f DG FunctionCallRequest event=%s", t, event)
                await _handle_function_calls(browser, dg, event)
            elif etype == "ConversationText":
                role = event.get("role")
                text = event.get("content") or event.get("text") or ""
                if text:
                    speaker = "agent" if role == "assistant" else "user"
                    logger.info(
                        "[lat] t=%.3f DG ConversationText speaker=%s text=%r",
                        t,
                        speaker,
                        text,
                    )
                    await browser.send_text(
                        json.dumps(
                            {"type": "transcript", "speaker": speaker, "text": text}
                        )
                    )
            elif etype == "Error" or etype == "Warning":
                logger.warning("[lat] t=%.3f DG %s: %s", t, etype, event)
            else:
                logger.info("[lat] t=%.3f DG event type=%s", t, etype)

    except websockets.WebSocketException:
        return


async def _handle_function_calls(
    browser: WebSocket,
    dg: websockets.WebSocketClientProtocol,
    event: dict[str, Any],
) -> None:
    """Forward each function call to the browser and ack Deepgram so the agent continues."""
    # Deepgram normally sends `{type:"FunctionCallRequest", functions:[{id,name,arguments},...]}`.
    # Tolerate a flat `{id, name, arguments}` payload too — some versions emit that.
    calls = event.get("functions")
    if not calls and event.get("name"):
        calls = [{k: event.get(k) for k in ("id", "name", "arguments", "client_side")}]

    for fn in calls or []:
        name = fn.get("name")
        fn_id = fn.get("id")
        raw_args = fn.get("arguments") or "{}"
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            args = {}

        # Tell the frontend — it already knows how to handle `change_slide`.
        logger.info(
            "[lat] t=%.3f → browser tool_call name=%s args=%s id=%s",
            time.monotonic(),
            name,
            args,
            fn_id,
        )
        await browser.send_text(
            json.dumps({"type": "tool_call", "name": name, "arguments": args})
        )

        # Ack the call so Deepgram's agent keeps flowing.
        await dg.send(
            json.dumps(
                {
                    "type": "FunctionCallResponse",
                    "id": fn_id,
                    "name": name,
                    "content": json.dumps({"ok": True}),
                }
            )
        )

        if name == "end_conversation":
            # Give the agent a beat to deliver its sign-off, then close.
            await asyncio.sleep(0.1)
            await browser.close(code=1000, reason="agent ended conversation")
