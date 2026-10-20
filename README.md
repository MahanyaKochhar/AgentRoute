# Agent Route

Dynamically Selecting Tools in Langchain Agent with OpenAI Decisions API in custom Middleware.

## Endpoints

| Endpoint | Tools available to Navigator | Routing |
|---|---|---|
| `POST /chat` | All 94 tools | None |
| `POST /v1/chat` | Tools scoring ≥ `TOOL_THRESHOLD` | One Decisions call per request |

Both agents share the model and prompt. Scores persist across model turns; each request starts fresh.
**All tools return static placeholders. No live healthcare searches run, as of now**

## Run

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # first setup only; preserve existing credentials
uvicorn src.main:app --reload
```

| Configuration | Purpose / default |
|---|---|
| `NAVIGATOR_API_KEY`, `NAVIGATOR_API_ENDPOINT`, `NAVIGATOR_MODEL` | Streaming, tool-capable answer model |
| `OPENAI_API_KEY` | Required for `/v1/chat` Decisions routing |
| `DECISION_MODEL` | `gpt-6-luna` |
| `TOOL_THRESHOLD` / `DECISION_TIMEOUT_SECONDS` | `0.5` / `30` seconds |
| `LANGFUSE_BASE_URL` | Local instance: `http://localhost:3000` |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | Langfuse project credentials |


## Try both routes

```bash
for route in chat v1/chat; do
  curl -N "http://localhost:8000/$route" \
    -H 'Content-Type: application/json' \
    -d '{"message":"Use dailymed_search_labels to look up Tylenol ingredients."}'
done
```

## Traces

- The resource creates one UUID string for the header, run ID, and metadata. Langfuse uses the same ID without hyphens.
- Root names: `chat.<approach>.<request_id>`. The LangChain callback records Navigator and tool steps.
- Decisions keeps its direct SDK call and records API-reported usage in one generation.

## Langfuse setup

1. Start the existing `agentroute-langfuse` stack in Docker Desktop. For a new installation, follow the [official Docker setup](https://langfuse.com/self-hosting/deployment/docker-compose).
2. Open [localhost:3000](http://localhost:3000), create an account and project, then generate project API keys.
3. Add the keys to the application's `.env`:

   ```dotenv
   LANGFUSE_BASE_URL=http://localhost:3000
   LANGFUSE_PUBLIC_KEY=your-project-public-key
   LANGFUSE_SECRET_KEY=your-project-secret-key
   ```

4. Restart FastAPI, send a chat request, and open **Tracing** in Langfuse. Match the trace to the response's `X-Request-ID` (without hyphens).

## Token cost comparison

**Result:** the routed request costs an estimated **$0.004708**, compared with **$0.038502** for all tools — **87.77% less** in this sample.

These estimates apply **GPT-6.1 Sol prices to recorded Gemma usage**. They are not actual GPT-6.1 Sol bills.

### Prices used

USD per **1 million tokens**, verified October 20, 2026; Standard short-context rates:

| API / assumed model | Input price | Output price |
|---|---:|---:|
| Navigator → [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) | $2.00 | $10.00 |
| [Decisions → GPT-6 Luna](https://developers.openai.com/api/docs/guides/decisions#pricing-and-availability) | $0.10 | $0.00 |

Decisions charges for input only. No cached input was recorded in these runs.

### Tokens recorded in Langfuse

Both endpoints received the same question:

> Use dailymed_search_labels to look up Tylenol ingredients.

Each invoked that tool once and made two Navigator calls. Counts below sum only generation observations; output includes reported reasoning tokens.

| Tokens | `/chat` — all tools | `/v1/chat` — routed |
|---|---:|---:|
| Navigator input | 18,661 | 613 |
| Navigator output | 118 | 128 |
| Decisions input | 0 | 22,018 |
| Decisions output | 0 | 0 |

### Estimated cost per request

For each API, multiply its token counts by its prices, then divide by 1,000,000.

| Cost component | `/chat` — all tools | `/v1/chat` — routed |
|---|---:|---:|
| Navigator input | $0.037322 | $0.001226 |
| Navigator output | $0.001180 | $0.001280 |
| Decisions input | $0.000000 | $0.002202 |
| Decisions output | $0.000000 | $0.000000 |
| **Total** | **$0.038502** | **$0.004708** |

**Saving: about $0.033794 per request (87.77%).** Routing sent more input tokens overall, but most went to the cheaper Decisions API.

### Timing and limitations

| Langfuse measurement | `/chat` — all tools | `/v1/chat` — routed |
|---|---:|---:|
| Request duration | 3.199 s | 4.628 s |
| Decisions duration | — | 1.853 s |

This is **one pair of requests**, measured October 20, 2026. Routing was cheaper under the assumed prices but slower in this sample. Navigator ran `gemma-4-31b-it`; GPT-6.1 Sol costs are used for frontier model comparisons.

[Recorded observations and exact calculations](results/langfuse-cost-comparison.json)
