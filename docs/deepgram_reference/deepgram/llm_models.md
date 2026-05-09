---
title: LLM Models
subtitle: >-
  An overview of the LLM providers and models you can use with the Voice Agent
  API.
slug: docs/voice-agent-llm-models
---

Defines the LLM (*Large Language Model*) to be used with your Agent. The `provider.type` field specifies the format or protocol of the API.

For example:

- `open_ai` means the API follows OpenAI's Chat Completions format.
- This option can be used with OpenAI, Azure OpenAI, or Amazon Bedrock — as long as the endpoint behaves like OpenAI's Chat Completion API.

<Info>
  You can set your Voice Agent's LLM model in the [Settings Message](/docs/configure-voice-agent) See the docs for more information.
</Info>

## Supported LLM providers

You can query the following endpoint to check the supported models for each provider:

```cURL
curl https://agent.deepgram.com/v1/agent/settings/think/models
```

### Example Payload

```json
{
  "models": [
    {
      "id": "gpt-5.5",
      "name": "GPT-5.5",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.4-nano",
      "name": "GPT-5.4 nano",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.4-mini",
      "name": "GPT-5.4 mini",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.4",
      "name": "GPT 5.4",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.3-chat-latest",
      "name": "GPT-5.3 Instant",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.2-chat-latest",
      "name": "GPT-5.2 Instant",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.2",
      "name": "GPT 5.2",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.1-chat-latest",
      "name": "GPT-5.1 Instant",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5.1",
      "name": "GPT-5.1 Thinking",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5-nano",
      "name": "GPT-5 nano",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5-mini",
      "name": "GPT-5 mini",
      "provider": "open_ai"
    },
    {
      "id": "gpt-5",
      "name": "GPT-5",
      "provider": "open_ai"
    },
    {
      "id": "gpt-4.1-nano",
      "name": "GPT-4.1 nano",
      "provider": "open_ai"
    },
    {
      "id": "gpt-4.1-mini",
      "name": "GPT-4.1 mini",
      "provider": "open_ai"
    },
    {
      "id": "gpt-4.1",
      "name": "GPT-4.1",
      "provider": "open_ai"
    },
    {
      "id": "gpt-4o-mini",
      "name": "GPT-4o mini",
      "provider": "open_ai"
    },
    {
      "id": "gpt-4o",
      "name": "GPT-4o",
      "provider": "open_ai"
    },
    {
      "id": "claude-sonnet-4-6",
      "name": "Claude Sonnet 4.6",
      "provider": "anthropic"
    },
    {
      "id": "claude-sonnet-4-5",
      "name": "Claude Sonnet 4.5",
      "provider": "anthropic"
    },
    {
      "id": "claude-4-5-haiku-latest",
      "name": "Claude Haiku 4.5",
      "provider": "anthropic"
    },
    {
      "id": "claude-3-5-haiku-latest",
      "name": "Claude Haiku 3.5",
      "provider": "anthropic"
    },
    {
      "id": "claude-sonnet-4-20250514",
      "name": "Claude Sonnet 4",
      "provider": "anthropic"
    },
    {
      "id": "gemini-3.1-flash-lite-preview",
      "name": "Gemini 3.1 Flash Lite",
      "provider": "google"
    },
    {
      "id": "gemini-3-flash-preview",
      "name": "Gemini 3.0 Flash Preview",
      "provider": "google"
    },
    {
      "id": "gemini-3-pro-preview",
      "name": "Gemini 3.0 Pro Preview",
      "provider": "google"
    },
    {
      "id": "gemini-2.5-flash",
      "name": "Gemini 2.5 Flash",
      "provider": "google"
    },
    {
      "id": "gemini-2.0-flash",
      "name": "Gemini 2.0 Flash",
      "provider": "google"
    },
    {
      "id": "gemini-2.5-flash-lite",
      "name": "Gemini 2.0 Flash Lite",
      "provider": "google"
    },
    {
      "id": "openai/gpt-oss-20b",
      "name": "GPT OSS 20B",
      "provider": "groq"
    },
    {
      "id": "nemotron-3-nano-30B-A3B",
      "name": "Nemotron 3 Nano 30B A3B",
      "provider": "nvidia"
    }
  ]
}

```

<Info>
   If you don't specify `agent.think.provider.type` the Voice Agent will use Deepgram's default managed LLMs. For managed LLMs, supported model names are predefined in our configuration.
</Info>

| Parameter                      | `open_ai` | `anthropic` | `aws_bedrock` | `google` | `groq` | `nvidia` |
| ------------------------------ | --------- | ----------- | -------- | ------ | --------- | -------- |
| `agent.think.provider.type`    | `open_ai` | `anthropic` | `aws_bedrock` | `google` | `groq` | `nvidia` |
| `agent.think.endpoint`         | optional  | optional    | required | optional | required | optional |

The `agent.think.endpoint` is optional or required based on the provider type:

* For `open_ai`, `anthropic`, `google`, and `nvidia`, the `endpoint` field is optional because Deepgram provides managed LLMs for these providers.
* For `groq` and `aws_bedrock` provider types, `endpoint` is required because Deepgram does not manage those LLMs.
* If an `endpoint` is provided the `url` is required but `headers` are optional.

<Info>
  When using `aws_bedrock` as the provider type, you must also provide AWS credentials in the `agent.think.provider.credentials` field. This should include:
  - `type`: Either "iam" or "sts"
  - `region`: AWS region (e.g., "us-east-2")
  - `access_key_id`: Your AWS access key ID
  - `secret_access_key`: Your AWS secret access key
  - `session_token`: Required only when `type` is "sts"
</Info>

## Supported LLM models

### OpenAI

| Provider                      | Model      | Pricing Tier |
| ------------------------------ | ---------- | ------------ |
| `open_ai`    | `gpt-5.5` | `Advanced` |
| `open_ai`    | `gpt-5.4-nano` | `Standard` |
| `open_ai`    | `gpt-5.4-mini` | `Standard` |
| `open_ai`    | `gpt-5.4` | `Advanced` |
| `open_ai`    | `gpt-5.3-chat-latest` | `Advanced` |
| `open_ai`    | `gpt-5.2-chat-latest` | `Advanced` |
| `open_ai`    | `gpt-5.2` | `Advanced` |
| `open_ai`    | `gpt-5.1-chat-latest` | `Advanced` |
| `open_ai`    | `gpt-5.1` | `Advanced` |
| `open_ai`    | `gpt-5-nano` | `Standard` |
| `open_ai`    | `gpt-5-mini` | `Standard` |
| `open_ai`    | `gpt-5` | `Advanced` |
| `open_ai`    | `gpt-4.1-nano` | `Standard` |
| `open_ai`    | `gpt-4.1-mini` | `Standard` |
| `open_ai`    | `gpt-4.1` | `Advanced` |
| `open_ai`    | `gpt-4o-mini` | `Standard` |
| `open_ai`    | `gpt-4o` | `Advanced` |

### Anthropic

| Provider                      | Model      | Pricing Tier |
| ------------------------------ | ---------- | ------------ |
| `anthropic`    | `claude-sonnet-4-6` | `Advanced` |
| `anthropic`    | `claude-sonnet-4-5` | `Advanced` |
| `anthropic`    | `claude-4-5-haiku-latest` | `Standard` |
| `anthropic`    | `claude-3-5-haiku-latest` | `Standard` |
| `anthropic`    | `claude-sonnet-4-20250514` | `Advanced` |

### Google

| Provider                      | Model      | Pricing Tier |
| ------------------------------ | ---------- | ------------ |
| `google`    | `gemini-3.1-flash-lite-preview` | `Standard` |
| `google`    | `gemini-3-flash-preview` | `Standard` |
| `google`    | `gemini-3-pro-preview` | `Advanced` |
| `google`    | `gemini-2.5-flash` | `Standard` |
| `google`    | `gemini-2.0-flash` | `Standard` (Deprecated) |
| `google`    | `gemini-2.0-flash-lite` | `Standard` |

#### Example using Deepgram's managed Google LLM

<CodeGroup>
``` json JSON
  // ... other settings ...
  "think": {
    "provider": {
      "type": "google",
      "model": "gemini-2.5-flash",
      "temperature": 0.5
    }
  }
  // ... other settings ...
```
</CodeGroup>

#### Example using a custom Google endpoint (BYO)

When using a custom endpoint, the `model` property is not supported.
The desired model is specified as part of the endpoint URL instead.

<Info>
Use [API keys](https://ai.google.dev/gemini-api/docs/api-key) from [Google AI Studio](https://aistudio.google.com/app/api-keys) for Gemini models. Keys from Vertex AI, Workspace Gemini, or Gemini Enterprise will not work with the Agent API.
</Info>

<CodeGroup>
``` json JSON
  // ... other settings ...
  "think": {
    "provider": {
      "type": "google",
      "temperature": 0.5
    },
    "endpoint": {
      "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse",
      "headers": {
        "x-goog-api-key": "xxxxxxxxx"
      }
    }
  }
  // ... other settings ...
```
</CodeGroup>

### NVIDIA

| Provider                      | Model      | Pricing Tier |
| ------------------------------ | ---------- | ------------ |
| `nvidia`    | `nemotron-3-nano-30B-A3B` | `Standard` |

#### Example using Deepgram's managed NVIDIA LLM

<CodeGroup>
``` json JSON
  // ... other settings ...
  "think": {
    "provider": {
      "type": "nvidia",
      "model": "nemotron-3-nano-30B-A3B",
      "temperature": 0.5
    }
  }
  // ... other settings ...
```
</CodeGroup>

### Groq

| Provider                      | Model      | Pricing Tier |
| ------------------------------ | ---------- | ------------ |
| `groq`    | `openai/gpt-oss-20b` | `Standard` |

## Example Payload

<CodeGroup>
  ```json JSON
  // ... other settings ...
   "think": {
        "provider": {
          "type": "open_ai",
          "model": "gpt-4o-mini",
          "temperature": 0.7
        },
        "endpoint": { // Optional if LLM provider is open_ai, anthropic, or google. Required for 3rd party LLM providers such as groq
          "url": "https://api.example.com/llm", // Required if endpoint is provided
          "headers": { // Optional if an endpoint is provided
            "authorization": "Bearer {{token}}"
          }
        },
      }
  // ... other settings ...
  ```
</CodeGroup>

## Passing a custom (BYO) LLM through a Cloud Provider

<Info>
  For Bring Your Own (BYO) LLMs, any model string provided is accepted without restriction.
</Info>

Deepgram tests against major LLM providers including OpenAI, Anthropic, and Google. When bringing your own LLM, you have two options:

- **Use an OpenAI-compatible LLM service or gateway.** Set `provider.type` to `open_ai` and point the `endpoint.url` to your service. Any LLM endpoint that conforms to the OpenAI Chat Completions API format will work, including third-party LLM gateways.
- **Use a custom endpoint from one of the supported major LLM providers.** If you have your own contract or deployment with a supported provider (such as OpenAI, Anthropic, or Google), set the `provider.type` to match that provider and supply your own `endpoint.url` and `endpoint.headers`.

In both cases, configure the `provider.type` to one of the supported provider values and set the `endpoint.url` and `endpoint.headers` fields to the correct values for your provider or gateway.

<CodeGroup>
  ```json JSON
    // ... other settings ...
  "think": {
        "provider": {
          "type": "open_ai",
          "model": "gpt-4",
          "temperature": 0.7
        },
        "endpoint": { // Required for a custom LLM
          "url": "https://cloud.provider.com/llm", // Required for a custom LLM
          "headers": { // Optional for a custom LLM
            "authorization": "Bearer {{token}}"
          }
        },
      }
    // ... other settings ...
  ```
</CodeGroup>

## Using multiple LLM providers

The `think` object accepts both a single provider and an array of providers. When you supply an array, the Voice Agent uses the providers as an ordered fallback chain: it sends each LLM request to the first provider in the list and automatically falls back to the next provider if the request fails.

### How fallback works

1. The agent sends the request to the **first** provider in the array.
2. If that provider returns an error or times out, the agent sends a [`THINK_REQUEST_FAILED`](/docs/voice-agent-warning) warning over the WebSocket and retries with the **next** provider.
3. This continues through every provider in the array.
4. If **all** providers fail, the agent sends a [`FAILED_TO_THINK`](/docs/voice-agent-errors) error and the turn produces no LLM response.

The fallback is per-request — each new conversational turn starts again from the first provider. Provider order matters, so place your preferred provider first and your most reliable fallback last.

<Info>
Fallback providers do not need to use the same `provider.type`. You can mix providers (for example, `open_ai` primary with an `anthropic` fallback) to maximize availability across independent infrastructure.
</Info>

### Example

```json JSON
{
  "agent": {
    "think": [
      {
        "provider": {
          "type": "open_ai",
          "model": "gpt-4o-mini",
          "temperature": 0.7
        }
      },
      {
        "provider": {
          "type": "anthropic",
          "model": "claude-4-5-haiku-latest",
          "temperature": 0.7
        }
      }
    ]
  }
}
```