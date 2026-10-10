# Stream

FastAPI chat API with LangChain, OpenAI Decisions tool routing, and SSE.
All application code is in `src/`. `ChatResource` constructs its `ChatService`
directly and registers `/chat` with a decorator; no lifespan initialization.

```text
main → ChatResource (owns ChatService) → agent → select_tools → tools
```

**Routing:** one Decisions invocation evaluates 94 named predicates against the
user request. Scores select tools using `TOOL_THRESHOLD` and are reused throughout
the agent run. The SDK can retry failed HTTP attempts. Each `/chat` starts a new
run; no conversation history is retained. Navigator generates the answer.

**Tools:** all 94 operations from Healthcare Public Data are static placeholders.
They return no live healthcare data. `jev_routing` preserves the Jev version;
`decision_routing` uses OpenAI Decisions.

**State:** `ChatState` extends LangChain's message state with the original
`request` and optional `tool_scores`. `state_schema=ChatState` registers those
fields with the agent so scores persist between model/tool steps, per request.

## Run

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

Set `NAVIGATOR_API_KEY`, `NAVIGATOR_API_ENDPOINT`, and `NAVIGATOR_MODEL` in `.env`.
Navigator must support streaming and tool calling. The OpenAI key is intentionally
blank: the app starts, but routing fails until `OPENAI_API_KEY` is configured.
Allow network access to `api.openai.com` for Decisions.

Defaults: `DECISION_MODEL=gpt-6-luna`, `DECISION_TIMEOUT_SECONDS=30`,
`TOOL_THRESHOLD=0.5`. Tune the threshold on labeled requests before production.

## Chat API

```bash
curl -N http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Find diabetes trials and publications."}'
```

SSE event sequence:

```text
response.created
response.output_text.delta  (repeated; append data.delta)
response.output_text.done   (data.text contains the accumulated text)
response.completed
```

Failures end with `response.failed`, with an error under `data.response.error`.
Every payload includes `type` and increasing `sequence_number`. Text events use
OpenAI SDK types; lifecycle events contain a compact Stream response summary,
not the full hosted Responses API object. Text from all agent model turns is
combined into one output item.

The SSE library handles heartbeats and disconnect cancellation; stalled writes
time out after 30 seconds. Streams have no replay/resume support. Browser clients
use streaming `fetch` for POST. Invalid input returns HTTP 422; errors after
streaming starts use events while HTTP remains 200. API docs: `/docs`.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use mocked models and Decisions responses, including the real OpenAI SDK
with a mock HTTP transport. No live API key is needed.

[Decisions guide](https://developers.openai.com/api/docs/guides/decisions)
