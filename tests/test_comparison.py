import json
import logging
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tests.test_chat import configured_agent, app, resource, service_module
from src.agent import build_agent
from src.metrics import RequestMetrics
from src.service import ChatService
from src.tools import HEALTHCARE_TOOLS


def metrics_records(caplog):
    return [json.loads(record.getMessage().removeprefix('metrics '))
            for record in caplog.records if record.getMessage().startswith('metrics ')]


def test_endpoints_compare_actual_agent_loops(configured_agent, monkeypatch, caplog):
    baseline, baseline_model, baseline_decisions = configured_agent(use_decisions=False)
    routed, routed_model, routed_decisions = configured_agent()
    monkeypatch.setattr(service_module, 'Settings', lambda: SimpleNamespace(navigator_model='test-model'))
    monkeypatch.setattr(service_module, 'build_agent',
                        lambda use_decisions: routed if use_decisions else baseline)
    monkeypatch.setattr(resource, 'service', ChatService(use_decisions=False))
    monkeypatch.setattr(resource, 'routed_service', ChatService(use_decisions=True))
    caplog.set_level(logging.INFO, logger='src')

    with TestClient(app) as client:
        responses = [client.post(path, json={'message': 'Find diabetes trials and publications.'})
                     for path in ('/chat', '/v1/chat')]
    for response in responses:
        assert response.status_code == 200
        assert 'event: response.completed' in response.text
        assert response.headers['x-request-id']
    assert responses[0].headers['x-request-id'] != responses[1].headers['x-request-id']
    assert not baseline_decisions.calls
    assert len(routed_decisions.calls) == 1
    assert baseline_model.bound_tools == [[tool.name for tool in HEALTHCARE_TOOLS]] * 2
    assert routed_model.bound_tools == [['pubmed_search_articles']] * 2

    records = metrics_records(caplog)
    for index, approach in enumerate(('all_tools', 'decisions')):
        request_id = responses[index].headers['x-request-id']
        records_for_request = [record for record in records if record['request_id'] == request_id]
        summary = next(r for r in records_for_request if r['event'] == 'request.completed')
        assert summary['approach'] == approach
        assert summary['status'] == 'completed'
        assert summary['model_calls'] == 2
        assert summary['model_input_tokens'] == 50
        assert summary['model_output_tokens'] == 7
        assert summary['decision_calls'] == index
        assert summary['decision_input_tokens'] == (1234 if index else 0)
        assert summary['decision_output_tokens'] == (2 if index else 0)
        assert summary['total_input_tokens'] == (1284 if index else 50)
        assert summary['total_output_tokens'] == (9 if index else 7)
        assert summary['latency_ms'] >= summary['first_text_ms'] >= 0
        assert len(summary['selected_tools']) == (1 if index else 94)
        assert [call['name'] for call in summary['tool_calls']] == ['pubmed_search_articles']
        calls = [r for r in records_for_request if r['event'] == 'api.call']
        assert len(calls) == 2 + index
        assert all(call['latency_ms'] >= 0 for call in calls)
        assert all(call['status'] == 'completed' for call in calls)


def test_both_agents_use_identical_prompt_and_only_routed_agent_has_middleware(monkeypatch):
    import src.agent as agent_module
    builds = []
    monkeypatch.setattr(agent_module, 'Settings', lambda: None)
    monkeypatch.setattr(agent_module, 'get_llm', lambda settings: 'same-model')
    monkeypatch.setattr(agent_module, 'create_agent', lambda **kwargs: builds.append(kwargs))
    build_agent(use_decisions=False)
    build_agent(use_decisions=True)
    assert builds[0]['system_prompt'] == builds[1]['system_prompt']
    assert builds[0]['tools'] is builds[1]['tools']
    assert builds[0]['model'] == builds[1]['model']
    assert builds[0]['middleware'] == []
    assert len(builds[1]['middleware']) == 1


def test_failed_decision_logs_latency_and_unknown_tokens(configured_agent, monkeypatch, caplog):
    import src.middleware as middleware_module
    from tests.test_chat import FakeDecisions, service_for

    class FailedDecisions(FakeDecisions):
        async def create(self, **kwargs):
            raise RuntimeError('upstream failed')

    agent, model, _ = configured_agent()
    monkeypatch.setattr(middleware_module, 'AsyncOpenAI', lambda **kwargs: FailedDecisions())
    service_for(monkeypatch, agent)
    caplog.set_level(logging.INFO, logger='src')
    with TestClient(app) as client:
        response = client.post('/v1/chat', json={'message': 'Find publications'})
    assert 'event: response.failed' in response.text
    assert not model.bound_tools
    records = metrics_records(caplog)
    call, summary = records
    assert call['kind'] == 'decision'
    assert call['status'] == summary['status'] == 'failed'
    assert call['error_type'] == 'RuntimeError'
    assert call['input_tokens'] is call['output_tokens'] is None
    assert summary['total_input_tokens'] is summary['total_output_tokens'] is None
    assert summary['model_calls'] == 0
    assert summary['decision_calls'] == 1


def test_missing_model_usage_is_not_reported_as_zero(caplog):
    import asyncio
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, LLMResult

    caplog.set_level(logging.INFO, logger='src')
    metrics = RequestMetrics('test-unknown', 'all_tools', 'test-model')
    async def run():
        await metrics.on_chat_model_start({}, [], run_id='call')
        await metrics.on_llm_end(LLMResult(generations=[[
            ChatGeneration(message=AIMessage(content='hello'))]]), run_id='call')
        metrics.finish('completed')
    asyncio.run(run())
    call, summary = metrics_records(caplog)
    assert call['input_tokens'] is call['output_tokens'] is None
    assert summary['total_input_tokens'] is summary['total_output_tokens'] is None


def test_model_failure_is_measured_on_baseline(configured_agent, monkeypatch, caplog):
    import src.agent as agent_module
    from tests.test_chat import ToolChatModel

    class FailedModel(ToolChatModel):
        def _stream(self, *args, **kwargs):
            raise RuntimeError('model unavailable')
            yield

    _, _, classifier = configured_agent(use_decisions=False)
    monkeypatch.setattr(agent_module, 'get_llm', lambda settings: FailedModel())
    agent = build_agent(use_decisions=False)
    monkeypatch.setattr(service_module, 'Settings', lambda: SimpleNamespace(navigator_model='test-model'))
    monkeypatch.setattr(service_module, 'build_agent', lambda **kwargs: agent)
    monkeypatch.setattr(resource, 'service', ChatService())
    caplog.set_level(logging.INFO, logger='src')
    with TestClient(app) as client:
        response = client.post('/chat', json={'message': 'Find publications'})
    assert 'event: response.failed' in response.text
    assert not classifier.calls
    call, summary = metrics_records(caplog)
    assert call['kind'] == 'model'
    assert call['status'] == summary['status'] == 'failed'
    assert call['error_type'] == 'RuntimeError'
    assert summary['model_calls'] == 1
    assert summary['decision_calls'] == 0
    assert summary['total_input_tokens'] is None


def test_benchmark_excludes_unknown_usage_and_failures():
    from scripts.compare_agents import summarize
    runs = [
        {'approach': 'all_tools', 'status': 'completed', 'expected_tools': ['search'],
         'exact_tool_match': True,
         'metrics': {'status': 'completed', 'latency_ms': 100, 'total_input_tokens': 50}},
        {'approach': 'all_tools', 'status': 'completed', 'expected_tools': ['search'],
         'exact_tool_match': False,
         'metrics': {'status': 'completed', 'latency_ms': 200, 'total_input_tokens': None}},
        {'approach': 'all_tools', 'status': 'failed', 'expected_tools': [],
         'metrics': {'status': 'failed', 'latency_ms': 1000, 'total_input_tokens': None}},
    ]
    summary = summarize(runs)['all_tools']
    assert summary['completed'] == 2
    assert summary['failed_or_unmeasured'] == 1
    assert summary['latency_ms']['mean'] == 150
    assert summary['latency_ms']['p95'] == 200
    assert summary['total_input_tokens']['mean'] == 50
    assert summary['total_input_tokens']['measured_requests'] == 1
    assert summary['exact_tool_match_rate'] == 0.5


@pytest.mark.asyncio
async def test_concurrent_agents_keep_metrics_separate(configured_agent, monkeypatch, caplog):
    import asyncio
    baseline, _, _ = configured_agent(use_decisions=False)
    routed, _, _ = configured_agent()
    monkeypatch.setattr(service_module, 'Settings', lambda: SimpleNamespace(navigator_model='test-model'))
    monkeypatch.setattr(service_module, 'build_agent',
                        lambda use_decisions: routed if use_decisions else baseline)
    services = [ChatService(use_decisions=False), ChatService(use_decisions=True)]
    caplog.set_level(logging.INFO, logger='src')
    async def run(index):
        return ''.join([text async for text in services[index].stream('Find publications', f'request-{index}')])
    texts = await asyncio.gather(run(0), run(1))
    assert texts == ['These are placeholder results.'] * 2
    summaries = {record['request_id']: record for record in metrics_records(caplog)
                 if record['event'] == 'request.completed'}
    assert summaries['request-0']['approach'] == 'all_tools'
    assert summaries['request-0']['decision_calls'] == 0
    assert summaries['request-0']['total_input_tokens'] == 50
    assert summaries['request-1']['approach'] == 'decisions'
    assert summaries['request-1']['decision_calls'] == 1
    assert summaries['request-1']['total_input_tokens'] == 1284


def test_unfinished_model_call_is_measured_as_cancelled(caplog):
    import asyncio
    caplog.set_level(logging.INFO, logger='src')
    metrics = RequestMetrics('cancelled-request', 'all_tools', 'test-model')
    asyncio.run(metrics.on_chat_model_start({}, [], run_id='unfinished'))
    metrics.finish('cancelled')
    call, summary = metrics_records(caplog)
    assert call['kind'] == 'model'
    assert call['status'] == summary['status'] == 'cancelled'
    assert call['latency_ms'] >= 0
    assert summary['model_calls'] == 1
    assert summary['model_input_tokens'] is None
