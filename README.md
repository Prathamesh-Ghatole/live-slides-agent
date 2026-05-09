# Live Slides Agent

A minimal website for **feline.ai** with a slide deck front and center and a voice agent the user can talk to about the slides. The agent narrates a 7-slide deck, advances slides automatically based on the conversation, and can be interrupted mid-sentence.

## Stack

- **Frontend:** HTML + JS (design mocked in [stitch.withgoogle.com](https://stitch.withgoogle.com))
- **Backend:** FastAPI
- **Slides:** static images generated with Gemini Canvas (`src/live_slides_agent/content/`)
- **Voice agents** (user picks one from the UI):
  - **Agent A — end-to-end:** Deepgram Voice Agent API
  - **Agent B — STT + LLM + TTS pipeline** via [`speech-to-speech`](https://pypi.org/project/speech-to-speech/):
    - STT: `parakeet-tdt` (local, MLX on Apple Silicon)
    - LLM: `google/gemini-3.1-flash-lite-preview` served through OpenRouter's OpenAI-compatible Responses API
    - TTS: `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` (local, MLX)

## Architecture

```mermaid
flowchart LR
    subgraph Browser
        UI[Slide viewer + Agent picker]
        Mic[Mic / Speaker]
    end

    subgraph FastAPI
        WS[/ws/voice]
    end

    subgraph Agents
        A[Agent A: Deepgram Voice Agent]
        B[Agent B: speech-to-speech<br/>parakeet-tdt → Responses API → Qwen3-TTS]
    end

    UI -- GET /slides/* --> FastAPI
    Mic <-- audio frames --> WS
    WS <-- change_slide tool-call --> UI
    WS <--> A
    WS <--> B
```

**Contract on `/ws/voice`**

- Carries bidirectional audio frames between the browser and the selected agent.
- Carries tool-calls from the agent back to the browser. Current tools:
  - `change_slide(index: int)` — browser advances the deck to `index`.
  - `finalize_order(customer_name, model, nearest_store_city, quantity?, deployment_window?, notes?)` — browser renders the final adoption order sheet overlay, which the user can save as a PNG or print and take to their nearest feline.ai store to redeem. No email is ever sent.
  - `end_conversation(item)` — browser closes the session after the agent's sign-off.
- Agent choice (`deepgram` or `local`) is sent as a query param when the WS connects, based on the user's selection in the UI.
- Barge-in / interrupt is handled by the voice agent's built-in VAD (Deepgram in Agent A, realtime-mode VAD in Agent B).

## Setup

```bash
cp .env.sample .env   # fill in OPENAI_API_KEY (OpenRouter), etc.
uv sync --extra voice # pulls in speech-to-speech for the bare-metal voice server on macOS
```

**Docker Desktop for Mac only:** enable host networking in
_Settings → Resources → Network → "Enable host networking"_. This lets the
webapp container reach the voice server on `localhost:8765` without any
env-var juggling. On Linux it's already on by default.

## Run

```bash
./run.sh
```

`run.sh` detects the OS:

- **macOS** → starts `scripts/run_speech_to_speech_server.sh` on the host (MLX), then `docker compose -f docker/compose.yml up` for the webapp.
- **Linux** → `docker compose -f docker/compose.yml -f docker/compose.linux.yml up` — both services containerized.

Open <http://localhost:8000>.

## Operational notes

- Containers run as a non-root `appuser`.
- WebSocket frames are capped at 64 MiB end-to-end (uvicorn `--ws-max-size` + `websockets.connect(max_size=…)` in the proxy).
- On macOS, `run.sh` pre-checks port 8765 and fails fast if a previous voice server is still listening. Clean up stragglers with:

  ```bash
  pkill -f 'speech-to-speech --mode realtime'
  ```

## Coming Soon

Planned agent capabilities beyond the current `change_slide`, `finalize_order`, and `end_conversation` tools:

- **`capture_tier_selection`** — record the user's choice of hardware tier (Onyx / Ember / Zenith) on Slide 5 to personalize the rest of the pitch, independent of order provisioning.
- **`log_objection`** — capture skepticism patterns ("it's just a cat," pricing pushback) for later review.
