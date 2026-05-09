"""
Bridge between the browser WebSocket and Deepgram's Voice Agent API.

Responsibilities:
- Open a WS to `wss://agent.deepgram.com/v1/agent/converse` with our API key.
- Send a `Settings` frame built by `agent.deepgram_config`.
- Forward raw PCM16 audio in both directions.
- Translate Deepgram's JSON events into the small contract our frontend already speaks:
    * `FunctionCallRequest` → `{type: "tool_call", name, arguments}` (and ack back to Deepgram)
    * `ConversationText`    → `{type: "transcript", speaker, text}`
  Everything else is logged and dropped.

All provider / model / voice configuration lives in
`agent/deepgram_config.py` — nothing in this file should need editing to
change models or voices.
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

from .agent.deepgram_config import settings_payload

logger = logging.getLogger(__name__)

DEEPGRAM_AGENT_URL = "wss://agent.deepgram.com/v1/agent/converse"

# Cap per-message size at 64 MiB. Plenty of headroom for realistic audio
# chunks from Deepgram while still defending against a client or upstream
# blasting unbounded frames at us. (The matching browser-side cap is
# applied via uvicorn's `--ws-max-size` flag; see Dockerfile.webapp.)
MAX_WS_MESSAGE_BYTES = 64 * 1024 * 1024


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
        await dg.send(json.dumps(settings_payload()))
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
