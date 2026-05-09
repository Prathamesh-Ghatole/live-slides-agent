#!/usr/bin/env bash
# One-shot launcher.
#   macOS  → voice server bare metal (MLX), webapp in docker
#   Linux  → both in docker containers
set -euo pipefail

OS="$(uname -s)"

COMPOSE_MAC=(-f docker/compose.yml)
COMPOSE_LINUX=(-f docker/compose.yml -f docker/compose.linux.yml)

cleanup() {
  # Kill the voice server's entire process group so the speech-to-speech
  # python workers die too (plain `kill $VOICE_PID` only reaps the shell).
  if [[ -n "${VOICE_PID:-}" ]] && kill -0 "$VOICE_PID" 2>/dev/null; then
    echo "[run.sh] stopping voice server (pgid $VOICE_PID)"
    kill -TERM -"$VOICE_PID" 2>/dev/null || true
    # Give it a moment, then SIGKILL anything left.
    sleep 2
    kill -KILL -"$VOICE_PID" 2>/dev/null || true
  fi
  # Also make sure docker compose tears down if we got here via a signal.
  docker compose "${COMPOSE_MAC[@]}" down --remove-orphans >/dev/null 2>&1 || true
}

case "$OS" in
  Darwin)
    echo "[run.sh] macOS detected → voice: bare metal, webapp: docker"
    # Fail fast if a previous run left the voice server alive.
    if lsof -nP -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
      echo "[run.sh] port 8765 is already in use — another voice server is running:"
      lsof -nP -iTCP:8765 -sTCP:LISTEN
      echo "[run.sh] kill it with:  pkill -f 'speech-to-speech --mode realtime'"
      exit 1
    fi
    # Enable job control so the backgrounded script gets its own process
    # group; that lets us kill the whole subtree on exit.
    set -m
    ./scripts/run_speech_to_speech_server.sh &
    VOICE_PID=$!
    trap cleanup EXIT INT TERM
    docker compose "${COMPOSE_MAC[@]}" up --build
    ;;
  Linux)
    echo "[run.sh] Linux detected → voice + webapp in docker"
    trap 'docker compose "${COMPOSE_LINUX[@]}" down --remove-orphans >/dev/null 2>&1 || true' EXIT INT TERM
    docker compose "${COMPOSE_LINUX[@]}" up --build
    ;;
  *)
    echo "[run.sh] Unsupported OS: $OS. macOS or Linux only." >&2
    exit 1
    ;;
esac
