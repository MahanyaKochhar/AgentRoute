# Agent Route

FastAPI chat API with LangChain, Jev tool routing, and SSE.
All application code is in `src/`. `ChatResource` creates its `ChatService`
directly and registers `/chat` with a decorator; no lifespan initialization.

```text
main → ChatResource (owns ChatService) → agent → select_tools → tools
```

**Routing:** one Jev invocation evaluates 94 named yes/no questions against the
user request. Scores select tools using `TOOL_THRESHOLD` and persist in
`ChatState` for the rest of the agent run. Every `/chat` starts a new run;
conversation history is not retained. Navigator generates the answer.

**Tools:** all 94 operations from Healthcare Public Data are static placeholders.
They return no live healthcare data. `decision_routing` offers the same API using
OpenAI Decisions predicates instead of Jev.

## Run

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

Set `NAVIGATOR_API_KEY`, `NAVIGATOR_API_ENDPOINT`, `NAVIGATOR_MODEL`, and
`TYPESAFE_API_KEY` in `.env`. Navigator must support streaming and tool calling.
Allow access to `api.typesafe.ai`, or configure a compatible `TYPESAFE_BASE_URL`.

Defaults: `JEV_MODEL=jev-latest`, `JEV_TIMEOUT_SECONDS=30`, `TOOL_THRESHOLD=0.5`.
The TypeSafe integration is pinned to its tested prerelease version.

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

Event names follow OpenAI's conventions; payloads are simple JSON objects:
`{"status":"in_progress"}`, `{"delta":"..."}`, `{"text":"..."}`, and
`{"status":"completed"}`. Failures end with `response.failed` and
`{"message":"Unable to complete the chat request."}`. The done event combines
text from all agent model turns.

The SSE library handles heartbeats and disconnect cancellation; stalled writes
time out after 30 seconds. Browser clients use streaming `fetch` for POST.
Invalid input returns HTTP 422; errors after streaming starts use events while
HTTP remains 200. No replay/resume support. API docs: `/docs`.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests mock Jev and chat models; no live API keys are required.

[Jev integration](https://docs.langchain.com/oss/python/integrations/providers/typesafe)
