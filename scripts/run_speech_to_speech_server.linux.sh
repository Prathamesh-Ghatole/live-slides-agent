#!/usr/bin/env bash
# Linux / CUDA entrypoint for the speech-to-speech voice server.
# Kept deliberately minimal — speech-to-speech auto-detects CUDA and picks
# sensible defaults on Linux. Tune later if/when we actually run this.
set -euo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${OPENAI_API_KEY:?OPENAI_API_KEY must be set (see .env.sample)}"
: "${OPENAI_API_BASE:?OPENAI_API_BASE must be set (see .env.sample)}"
: "${OPENAI_DEFAULT_MODEL:?OPENAI_DEFAULT_MODEL must be set (see .env.sample)}"

uv run speech-to-speech \
    --mode realtime \
    --llm_backend responses-api \
    --model_name "$OPENAI_DEFAULT_MODEL" \
    --responses_api_api_key "$OPENAI_API_KEY" \
    --responses_api_base_url "$OPENAI_API_BASE" \
    --responses_api_stream \
    --stt parakeet-tdt \
    --tts qwen3 \
    --qwen3_tts_model_name Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
    --chat_size 30 \
    --enable_live_transcription \
    --thresh 0.6
