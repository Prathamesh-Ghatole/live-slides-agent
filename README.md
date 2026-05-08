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
- Carries tool-calls from the agent back to the browser. For now the only tool is:
  - `change_slide(index: int)` — browser advances the deck to `index`.
- Agent choice (`deepgram` or `local`) is sent as a query param when the WS connects, based on the user's selection in the UI.
- Barge-in / interrupt is handled by the voice agent's built-in VAD (Deepgram in Agent A, realtime-mode VAD in Agent B).

## Setup

```bash
uv sync
cp .env.sample .env   # fill in OPENAI_API_KEY (OpenRouter), etc.
```

## Run

```bash
# Agent B voice pipeline
./run_speech_to_speech_server.sh

# FastAPI app (coming soon)
uv run uvicorn live_slides_agent.app:app --reload
```
