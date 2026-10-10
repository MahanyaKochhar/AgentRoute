"""Per-request API measurements using callbacks and standard Python logging."""
import json
import logging
from asyncio import CancelledError
from contextvars import ContextVar
from time import perf_counter

from langchain_core.callbacks import AsyncCallbackHandler

logger = logging.getLogger(__name__)
current_metrics: ContextVar = ContextVar("chat_metrics", default=None)


def token_count(usage, name):
    return usage.get(name) if isinstance(usage, dict) else getattr(usage, name, None)


class RequestMetrics(AsyncCallbackHandler):
    def __init__(self, request_id, approach, model):
        self.request_id = request_id
        self.approach = approach
        self.model = model
        self.started = perf_counter()
        self.first_text_ms = None
        self.calls = []
        self.model_starts = {}
        self.tool_calls = []
        self.selected_tools = []

    def emit(self, event, **fields):
        record = {"event": event, "request_id": self.request_id,
                  "approach": self.approach, **fields}
        logger.info("metrics %s", json.dumps(record))
        return record

    def api_call(self, kind, model, started, usage=None, status="completed", error=None):
        record = self.emit(
            "api.call", kind=kind, model=model,
            call_index=sum(call["kind"] == kind for call in self.calls) + 1,
            input_tokens=token_count(usage, "input_tokens"),
            output_tokens=token_count(usage, "output_tokens"),
            latency_ms=round((perf_counter() - started) * 1000, 2),
            status=status, error_type=type(error).__name__ if error else None,
        )
        self.calls.append(record)

    async def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        self.model_starts[run_id] = perf_counter()

    async def on_llm_end(self, response, *, run_id, **kwargs):
        usage = None
        if response.generations and response.generations[0]:
            message = getattr(response.generations[0][0], "message", None)
            usage = getattr(message, "usage_metadata", None)
        if usage is None and response.llm_output:
            raw = response.llm_output.get("token_usage", {})
            usage = {"input_tokens": raw.get("prompt_tokens"),
                     "output_tokens": raw.get("completion_tokens")}
        self.api_call("model", self.model, self.model_starts.pop(run_id), usage)

    async def on_llm_error(self, error, *, run_id, **kwargs):
        started = self.model_starts.pop(run_id, perf_counter())
        self.api_call("model", self.model, started,
                      status="cancelled" if isinstance(error, CancelledError) else "failed", error=error)

    async def on_tool_start(self, serialized, input_str, *, run_id, inputs=None, **kwargs):
        self.tool_calls.append({"name": serialized.get("name"),
                                "args": inputs if inputs is not None else input_str})

    def finish(self, status):
        # Some providers do not emit a final callback when a stream is cancelled.
        for started in self.model_starts.values():
            self.api_call("model", self.model, started, status=status)
        self.model_starts.clear()

        def total(kind, field):
            calls = [call for call in self.calls if call["kind"] == kind]
            values = [call[field] for call in calls]
            return sum(values) if all(value is not None for value in values) else None

        counts = {kind: sum(call["kind"] == kind for call in self.calls)
                  for kind in ("model", "decision")}
        totals = {f"{kind}_{field}": total(kind, field)
                  for kind in counts for field in ("input_tokens", "output_tokens")}
        for field in ("input_tokens", "output_tokens"):
            values = [totals[f"{kind}_{field}"] for kind in counts]
            totals[f"total_{field}"] = sum(values) if all(v is not None for v in values) else None
        self.emit("request.completed", status=status,
                  latency_ms=round((perf_counter() - self.started) * 1000, 2),
                  first_text_ms=self.first_text_ms, model_calls=counts["model"],
                  decision_calls=counts["decision"], selected_tools=self.selected_tools,
                  tool_calls=self.tool_calls, **totals)
