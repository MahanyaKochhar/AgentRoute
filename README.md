# Stream

FastAPI `POST /chat` backed by a LangChain agent. Jev selects relevant healthcare
tools from the user request, and the response streams as Server-Sent Events (SSE).

## Code layout

All application code lives directly in `src/`:

- `main.py`: FastAPI app and service initialization at startup.
- `resource.py`: validates the chat request and returns an SSE response.
- `service.py`: owns the agent and streams its response text.
- `streaming.py`: converts text into native JSON SSE events.
- `agent.py`: parameterless `build_agent()` using the configured model and Jev.
- `middleware.py`: async `@wrap_model_call` decorator, passed directly as `middleware=[select_tools]`.
- `tools.py`: all static Healthcare Public Data tool operations.
- `state.py`: messages, the original request, and per-run routing scores.
- `navigator_llm.py`: streaming LangChain adapter for the Navigator gateway.
- `settings.py`: environment settings.

## Routing

The middleware sends `state["request"]` and one named yes/no `Noul` question per
tool to `TypeSafeClassifier` in a single async invocation. Jev evaluates the
questions independently in parallel. Tools with relevance probability at least
`TOOL_THRESHOLD` are exposed with `request.override(tools=selected_tools)`.
Zero, one, or multiple tools can qualify.

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
`NAVIGATOR_MODEL`, plus `TYPESAFE_API_KEY`, in `.env`. Navigator must support
streaming chat completions and tool calling. Its endpoint can be a base URL or
full `.../v1/chat/completions` URL; normalization preserves `/v1`.

Get a Jev API key from [TypeSafe](https://console.typesafe.ai). The classifier
reads `TYPESAFE_API_KEY` and optional `TYPESAFE_BASE_URL` directly. The original
request is sent to Jev for routing and Navigator for answering. Optional settings:

| Setting | Default |
| --- | --- |
| `JEV_MODEL` | `jev-latest` |
| `JEV_TIMEOUT_SECONDS` | `30` |
| `TOOL_THRESHOLD` | `0.5` (in `(0, 1]`) |

The TypeSafe integration is a prerelease; its tested version is pinned in
`requirements.txt`. No LangGraph dev server or LangSmith key is required.

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

Tests patch configured dependencies with fake classifiers and chat models while
exercising the real LangChain agent and FastAPI endpoint. They check catalogue
coverage, batched scoring, tool selection and execution, score reuse, concurrent
request isolation, streamed text, validation, error events, and disconnects.
No API keys or paid API requests are needed for these tests.

Implementation references:
[Building a Harness with Jev](https://www.langchain.com/blog/building-a-harness-with-jev),
[TypeSafe integration](https://docs.langchain.com/oss/python/integrations/providers/typesafe),
[LangChain wrap-style hooks](https://docs.langchain.com/oss/python/langchain/middleware/custom#wrap-style-hooks).
