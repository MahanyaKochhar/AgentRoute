# Stream

FastAPI `POST /chat` backed by a LangChain agent. OpenAI Decisions predicates select relevant healthcare
tools from the user request, and the response streams as Server-Sent Events (SSE).

## Code layout

All application code lives directly in `src/`:

- `main.py`: FastAPI app and service initialization at startup.
- `resource.py`: validates the chat request and returns an SSE response.
- `service.py`: owns the agent and streams its response text.
- `streaming.py`: converts text into native JSON SSE events.
- `agent.py`: parameterless `build_agent()` using Navigator and `middleware=[select_tools]`.
- `middleware.py`: async `@wrap_model_call` decorator, passed directly as `middleware=[select_tools]`.
- `tools.py`: all static Healthcare Public Data tool operations.
- `state.py`: messages, the original request, and per-run routing scores.
- `navigator_llm.py`: streaming LangChain adapter for the Navigator gateway.
- `settings.py`: environment settings.

## Routing

The decorated `select_tools` middleware sends `state["request"]` as shared input
and one named `predicate` per tool in a single `AsyncOpenAI.decisions.create`
request. Each question asks whether the tool's specific capabilities are useful
for the request. Tools whose probability meets `TOOL_THRESHOLD` are exposed with
`request.override(tools=selected_tools)`. Zero, one, or several tools can qualify.

Answers are matched by tool name. Refusals, missing or duplicate answers, and
invalid probabilities stop routing and produce the standard SSE error event.
The SDK client closes after classification and uses a 30-second timeout with up
to two retries. Navigator remains the model that generates the response.

All tools are registered when the agent is built so selected tools can execute.
Scores are saved in the individual run's state with `ExtendedModelResponse` and
`Command`; subsequent model calls reuse them. Concurrent requests have separate
routing state. Each API request starts an independent conversation.

## Healthcare Public Data tools

The installed plugin declares nine connector families with **94 tool operations**.
Every exposed operation has a corresponding static tool, retaining its
connector-prefixed name. For example, PubMed has separate `pubmed_search_articles`,
`pubmed_get_articles`, and `pubmed_get_full_text_articles` tools rather than a
single family-level placeholder.

| Connector family | Tools |
| --- | ---: |
| ClinicalTrials.gov | 7 |
| PubMed | 7 |
| DailyMed | 4 |
| RxNorm | 4 |
| openFDA | 32 |
| NPI Registry | 3 |
| Medicare Care Compare | 9 |
| CMS Coverage | 17 |
| CMS Open Data | 11 |
| **Total** | **94** |

The catalogue was checked against the installed Healthcare Public Data plugin on
October 7, 2026. The verified names are recorded in
`tests/fixtures/healthcare_tool_names.json`, and a test checks complete coverage.

Each tool accepts a simple `query` string and returns a fixed string such as
`pubmed_search_articles: static placeholder response.` No connector APIs are
called. The agent identifies these results as demonstrations, not live evidence.

## Setup

Use Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set the existing `NAVIGATOR_API_KEY`, `NAVIGATOR_API_ENDPOINT`, and
`NAVIGATOR_MODEL` in `.env`. Navigator must support streaming chat completions and
tool calling. Its endpoint can be a base URL or full `.../v1/chat/completions` URL;
normalization preserves `/v1`.

`OPENAI_API_KEY` is intentionally blank in `.env.example`, and settings default
to a blank key. The app can start in this state, but `/chat` emits an SSE error
until a key is configured. No placeholder credential is sent to OpenAI. Routing
uses `https://api.openai.com/v1/decisions`; the deployment needs network access
to `api.openai.com`. The original request is sent to OpenAI for routing and to
Navigator for answering.

| Setting | Default |
| --- | --- |
| `OPENAI_API_KEY` | blank |
| `DECISION_MODEL` | `gpt-6-luna` |
| `DECISION_TIMEOUT_SECONDS` | `30` |
| `TOOL_THRESHOLD` | `0.5` (in `(0, 1]`) |

The threshold is an initial configurable value, not a calibrated accuracy claim.
Before production, tune it on labeled requests to balance missed relevant tools
against unnecessary tool exposure, as recommended in the
[Decisions guide](https://developers.openai.com/api/docs/guides/decisions).
The OpenAI SDK version supporting Decisions is pinned in `requirements.txt`.
No LangGraph dev server or LangSmith key is required.

The `jev_routing` branch preserves the Jev implementation. This branch,
`decision_routing`, replaces the router with OpenAI Decisions.

## Run

From the repository root:

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: `http://127.0.0.1:8000/docs`.

```bash
curl -N --request POST http://127.0.0.1:8000/chat \
  --header 'Content-Type: application/json' \
  --header 'Accept: text/event-stream' \
  --data '{"message":"Find clinical trials and publications about diabetes."}'
```

The response is `text/event-stream`, with named events and JSON data:

```text
event: token
data: {"text":"These are "}

event: token
data: {"text":"placeholder results."}

event: done
data: {"status":"complete"}
```

Concatenate each `token` event's `text`. Chunks can contain multiple tokens.
Only response text is streamed; reasoning blocks, tool arguments, and raw tool
results are excluded. Stream failures emit an `error` event instead of `done`:

```text
event: error
data: {"message":"Unable to complete the chat request."}
```

Validation errors return HTTP 422 before streaming. Messages must be nonblank
strings of at most 20,000 characters; extra fields are rejected. Configuration
errors fail at startup. Failures after streaming begins cannot change HTTP 200.

`EventSourceResponse` handles heartbeats, disables caching, and cancels on disconnect.
Stalled writes time out after 30 seconds, and proxy buffering is disabled. The small
streaming helper uses native `JSONServerSentEvent` serialization and closes the
text iterator with `aclosing`. Use streaming `fetch` for browser POST requests;
native `EventSource` sends GET requests.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests patch configured dependencies with fake Decisions clients and chat models while
exercising the real LangChain agent and FastAPI endpoint. They check catalogue
coverage, batched scoring, tool selection and execution, score reuse, concurrent
request isolation, streamed text, validation, error events, and disconnects.
A transport-level test also exercises the actual OpenAI SDK against a mock HTTP
response. No API keys or paid API requests are needed for these tests.

Implementation references:
[OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions),
[LangChain wrap-style hooks](https://docs.langchain.com/oss/python/langchain/middleware/custom#wrap-style-hooks).
