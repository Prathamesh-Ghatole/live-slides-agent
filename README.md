# Live Slides Agent

A minimal website for **feline.ai** with a slide deck front and center and a voice agent the user can talk to about the slides. The agent narrates a 7-slide deck, advances slides automatically based on the conversation, and can be interrupted mid-sentence.

## Stack

- **Frontend:** HTML + JS (design mocked in [stitch.withgoogle.com](https://stitch.withgoogle.com))
- **Backend:** FastAPI
- **Slides:** static images generated with Gemini Canvas (`src/live_slides_agent/content/`)
- **Voice agent:** end-to-end via the [Deepgram Voice Agent API](https://developers.deepgram.com/docs/voice-agent) — STT, LLM, and TTS are all handled by Deepgram's managed endpoint. Provider/model/voice knobs live in `src/live_slides_agent/agent/deepgram_config.py`.

## Architecture

```mermaid
flowchart LR
    subgraph Browser
        UI[Slide viewer]
        Mic[Mic / Speaker]
    end

    subgraph FastAPI
        WS[/ws/voice]
    end

    A[Deepgram Voice Agent API]

    UI -- GET /slides/* --> FastAPI
    Mic <-- audio frames --> WS
    WS <-- change_slide tool-call --> UI
    WS <--> A
```

**Contract on `/ws/voice`**

- Carries bidirectional audio frames between the browser and the Deepgram voice agent.
- Carries tool-calls from the agent back to the browser. Current tools:
  - `change_slide(index: int)` — browser advances the deck to `index`.
  - `finalize_order(customer_name, model, nearest_store_city, quantity?, deployment_window?, notes?)` — browser renders the final adoption order sheet overlay, which the user can save as a PNG or print and take to their nearest feline.ai store to redeem. No email is ever sent.
  - `end_conversation(item)` — browser closes the session after the agent's sign-off.
- Barge-in / interrupt is handled by Deepgram's built-in VAD.

## Setup

```bash
cp .env.sample .env   # fill in DEEPGRAM_API_KEY
```

## Run

```bash
./run.sh
```

`run.sh` is a thin wrapper around `docker compose -f docker/compose.yml up --build` and works identically on macOS and Linux.

Open <http://localhost:8000>.

## Operational notes

- Container runs as a non-root `appuser`.
- WebSocket frames are capped at 64 MiB end-to-end (uvicorn `--ws-max-size` + `websockets.connect(max_size=…)` in the Deepgram bridge).

## Coming Soon

Planned agent capabilities beyond the current `change_slide`, `finalize_order`, and `end_conversation` tools:

- **`capture_tier_selection`** — record the user's choice of hardware tier (Onyx / Ember / Zenith) on Slide 5 to personalize the rest of the pitch, independent of order provisioning.
- **`log_objection`** — capture skepticism patterns ("it's just a cat," pricing pushback) for later review.
