#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from .env if present
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
    --qwen3_tts_speaker Aiden \
    --qwen3_tts_language auto \
    --qwen3_tts_non_streaming_mode True \
    --qwen3_tts_mlx_quantization 6bit \
    --chat_size 30 \
    --enable_live_transcription \
    --thresh 0.6
