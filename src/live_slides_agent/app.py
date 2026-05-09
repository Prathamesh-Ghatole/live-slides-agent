"""
Minimal FastAPI app for Live Slides Agent.

Responsibilities (current scope):
- Serve the static frontend (index.html + slide images).
- Proxy /ws/voice to the `speech-to-speech` WebSocket server running on
  localhost:8765 (bare metal on macOS, a sibling container on Linux with
  host networking).

The FastAPI proxy exists so the browser has a single origin and so we can
eventually intercept tool-calls (e.g. `change_slide`) before forwarding to
the UI.
"""

from __future__ import annotations

import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .voice_deepgram import bridge_deepgram

load_dotenv(override=False)


def _setup_logging() -> None:
    """Log to console (as before) and tee to logs/live-slides-agent.log."""
    root = logging.getLogger()
    if getattr(root, "_lsa_file_handler_attached", False):
        return  # idempotent across reloads

    root.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Console — keep uvicorn's existing stderr handler; only add one if none.
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)

    # File — logs/ dir is resolvable from $LSA_LOG_DIR or the project root.
    log_dir = Path(os.environ.get("LSA_LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(
        log_dir / "live-slides-agent.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    root.addHandler(fh)
    root._lsa_file_handler_attached = True  # type: ignore[attr-defined]


_setup_logging()
logger = logging.getLogger(__name__)

# With host networking (see docker-compose.yml), localhost inside the
# container is the host, so this reaches the voice server on either OS.
VOICE_WS_URL = "ws://localhost:8765"

# Cap per-message size at 64 MB. Plenty of headroom for realistic audio
# chunks from `speech-to-speech` while still defending against a client or
# upstream blasting unbounded frames at us. (The matching browser-side cap
# is applied via uvicorn's `--ws-max-size` flag; see Dockerfile.webapp.)
MAX_WS_MESSAGE_BYTES = 64 * 1024 * 1024

PKG_DIR = Path(__file__).resolve().parent
STATIC_DIR = PKG_DIR / "static"
CONTENT_DIR = PKG_DIR / "content"

app = FastAPI(title="Live Slides Agent")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Slide images live alongside the package in content/1.jpg .. 7.jpg
app.mount("/slides", StaticFiles(directory=CONTENT_DIR), name="slides")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.websocket("/ws/voice")
async def voice_proxy(ws: WebSocket) -> None:
    """Bidirectional proxy between the browser and the selected voice agent."""
    await ws.accept()
    agent = ws.query_params.get("agent", "local")
    logger.info("browser connected; agent=%s", agent)

    if agent == "deepgram":
        await bridge_deepgram(ws)
        return

    try:
        async with websockets.connect(
            VOICE_WS_URL, max_size=MAX_WS_MESSAGE_BYTES
        ) as upstream:
            await _pipe(ws, upstream)
    except (OSError, websockets.WebSocketException) as exc:
        logger.warning("voice upstream unreachable: %s", exc)
        await ws.close(code=1011, reason="voice server unavailable")


async def _pipe(
    browser: WebSocket, upstream: websockets.WebSocketClientProtocol
) -> None:
    async def browser_to_upstream() -> None:
        try:
            while True:
                msg = await browser.receive()
                if msg["type"] == "websocket.disconnect":
                    return
                if (data := msg.get("bytes")) is not None:
                    await upstream.send(data)
                elif (text := msg.get("text")) is not None:
                    await upstream.send(text)
        except WebSocketDisconnect:
            return

    async def upstream_to_browser() -> None:
        try:
            async for msg in upstream:
                if isinstance(msg, (bytes, bytearray)):
                    await browser.send_bytes(bytes(msg))
                else:
                    await browser.send_text(msg)
        except websockets.WebSocketException:
            return

    done, pending = await asyncio.wait(
        {
            asyncio.create_task(browser_to_upstream()),
            asyncio.create_task(upstream_to_browser()),
        },
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    for task in done:
        # surface any unexpected exception in logs
        if (exc := task.exception()) is not None:
            logger.warning("proxy task ended with %s", exc)
