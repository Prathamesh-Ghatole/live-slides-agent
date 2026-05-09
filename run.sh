#!/usr/bin/env bash
# One-shot launcher: spin up the webapp (Deepgram-backed voice agent) via
# docker compose. Same command works on macOS and Linux.
set -euo pipefail

COMPOSE=(-f docker/compose.yml)

trap 'docker compose "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true' EXIT INT TERM

docker compose "${COMPOSE[@]}" up --build
