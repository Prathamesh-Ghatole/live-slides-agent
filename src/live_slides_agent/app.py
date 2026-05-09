"""
Minimal FastAPI app for Live Slides Agent.

Responsibilities (current scope):
- Serve the static frontend (index.html + slide images).
- Bridge /ws/voice through to Deepgram's Voice Agent API via
  `voice_deepgram.bridge_deepgram`.

The FastAPI app exists so the browser has a single origin and so we can
intercept tool-calls (e.g. `change_slide`) before forwarding them to the
UI.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
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
    """Bidirectional bridge between the browser and the Deepgram voice agent."""
    await ws.accept()
    logger.info("browser connected; bridging to Deepgram voice agent")
    await bridge_deepgram(ws)
