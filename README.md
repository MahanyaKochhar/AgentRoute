# Agent Route

FastAPI chat API with LangChain, OpenAI Decisions tool routing, and SSE.
All application code is in `src/`. `ChatResource` constructs its `ChatService`
directly and registers two routes; no lifespan initialization.

```text
POST /chat    → all-tools agent → Navigator → tools
POST /v1/chat → routed agent → Decisions → Navigator → selected tools
```

Both agents use the same Navigator model, system prompt, tool catalogue, and fresh
request state. `/chat` exposes all 94 tools and has no middleware. `/v1/chat` uses
`select_tools` middleware.

**Routing on `/v1/chat`:** one Decisions invocation evaluates 94 named predicates against the
user request. Scores select tools using `TOOL_THRESHOLD` and are reused throughout
the agent run. The SDK can retry failed HTTP attempts. Each request starts a new
run; no conversation history is retained. Navigator generates the answer.

**Tools:** all 94 operations from Healthcare Public Data are static placeholders.
They return no live healthcare data.

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
blank: `/chat` works without it, but `/v1/chat` routing requires `OPENAI_API_KEY`.
Allow network access to `api.openai.com` for Decisions.

Defaults: `DECISION_MODEL=gpt-6-luna`, `DECISION_TIMEOUT_SECONDS=30`,
`TOOL_THRESHOLD=0.5`. Tune the threshold on labeled requests before production.

## Chat API

```bash
curl -N http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Find diabetes trials and publications."}'

curl -N http://127.0.0.1:8000/v1/chat \
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
time out after 30 seconds. SSE connections have no replay/resume support. Browser clients
use streaming `fetch` for POST. Invalid input returns HTTP 422; errors after
streaming starts use events while HTTP remains 200. API docs: `/docs`.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use mocked models and Decisions responses, including the real OpenAI SDK
with a mock HTTP transport. No live API key is needed.

## INFO logs and comparison

`src/logger.py` configures INFO logging to `logs/app.log` under the project root,
with application logs excluded from the console. Logs include selected tool names,
actual tool calls with arguments, errors with tracebacks, and structured `metrics`
JSON records. Each response includes an `X-Request-ID` header correlating its logs.
Decisions answers, tool results, and routine model/chat progress are not logged.

`api.call` records measure every Navigator turn and Decisions invocation: approach,
request ID, model, input tokens, output tokens, latency in milliseconds, and status.
LangChain callbacks measure model calls without adding logging middleware. Navigator
streaming requests ask the gateway to include token usage. Missing usage is `null`,
not an estimate or zero. Failed calls also record latency and error type; usage
is usually unavailable. SDK retries are included in call latency and are not
separate application invocations; unreported token usage from failed attempts
cannot be included in totals.

`request.completed` records include status (completed/failed/cancelled), duration,
time to first text, model/Decisions call counts, selected and executed tools,
separate model and Decisions token totals, and combined input/output token totals.
Request duration covers the service stream, including routing, model calls, tools,
and streaming backpressure; it excludes HTTP validation and the final SSE framing.
The benchmark separately measures client duration through the full SSE response.
No Decisions calls on `/chat` means its Decisions totals are zero. Missing usage
from any invoked API makes the corresponding aggregate `null`.
These are server diagnostics; they are not added to the SSE response.
Application modules use standard Python `logging.getLogger(__name__)` and
`logger.info(...)`. Tool functions log directly through their placeholder helper;
there is no logging middleware.

Run the reproducible simulation without external API requests:

```bash
python -m pytest tests/test_chat.py::test_simulate_diabetes_chat -q -s
```

It posts `{"message":"Find diabetes trials and publications."}` through the actual
`/v1/chat` route and agent loop, with mocked Decisions and Navigator responses. The
mock assigns 0.5 to `clinicaltrials_gov_search_trials` and `pubmed_search_articles`,
and 0.1 to the other 92 predicates. These are illustrative scores, not live results.
The printed trace shows metrics, selected tools, and executed calls only.

1. `/v1/chat` starts SSE and the service creates fresh request state.
2. `select_tools` invokes Decisions before the first Navigator call, validates the
   94 answers, and exposes tools scoring at least `TOOL_THRESHOLD` to Navigator.
3. Navigator chooses tool calls and arguments. Selection alone does not execute tools.
4. The agent executes requested tools and adds their results as tool messages.
5. Before the next Navigator turn, middleware reuses stored scores without another
   Decisions invocation. Navigator receives the tool results and generates text.
6. Text streams as SSE deltas, followed by done/completed events.

This simulation verifies one Decisions invocation, two Navigator turns, and two
placeholder tool executions. Live scores, tool calls, ordering, and number of turns
depend on the APIs' responses; the SDK may retry Decisions HTTP attempts.

With the server running, run paired real API comparisons:

```bash
python scripts/compare_agents.py --repeats 3 \
  --expected-tool clinicaltrials_gov_search_trials \
  --expected-tool pubmed_search_articles
```

This sends six live requests, alternates endpoint order, and writes
`logs/comparison.json` with responses, per-call metrics, success counts, token
totals, mean/median/p95 latencies, measurement coverage, and exact tool-set match
rates against the supplied expected tools. The console prints a comparison table.
Use `--message`, `--expected-tool`, and `--output` to repeat across labeled queries.
Include Decisions tokens and latency when judging routing savings. Failures are
reported separately from completed-request averages. Small samples, provider
caching, model variability, and placeholder tools limit conclusions; inspect saved
responses and tool choices as well as token/latency statistics. Exact tool-set match
is only a routing check, not a measure of answer quality. No pricing is assumed.

[Decisions guide](https://developers.openai.com/api/docs/guides/decisions)
