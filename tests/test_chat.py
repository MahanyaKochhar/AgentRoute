import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from langchain.agents.middleware import ModelRequest, ModelResponse
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field, SecretStr

import src.agent as agent_module
import src.service as service_module
import src.middleware as middleware_module
from unittest.mock import patch

# Resource construction is eager; replace model assembly before importing the app.
with patch("src.service.build_agent", return_value=None):
    from src.main import app
    from src.resource import resource
from src.middleware import select_tools
from src.navigator_llm import get_llm
from src.service import ChatService
from src.settings import Settings
from src.tools import HEALTHCARE_TOOLS


class FakeDecisions:
    def __init__(self, selected=('pubmed_search_articles',)):
        self.selected = selected
        self.calls = []

    @property
    def decisions(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def create(self, **request):
        await asyncio.sleep(0)
        self.calls.append(request)
        return SimpleNamespace(answers=[
            SimpleNamespace(type="predicate", name=q["name"],
                            probability=0.5 if q["name"] in self.selected else 0.1)
            for q in request["questions"]
        ])


class ToolChatModel(BaseChatModel):
    bound_tools: list[list[str]] = Field(default_factory=list)
    call_tool: bool = True

    @property
    def _llm_type(self):
        return 'test-chat'

    def bind_tools(self, tools, **kwargs):
        self.bound_tools.append([tool.name for tool in tools])
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self.call_tool and not any(isinstance(m, ToolMessage) for m in messages):
            response = AIMessage(content='', tool_calls=[{
                'name': 'pubmed_search_articles', 'args': {'query': 'diabetes'}, 'id': 'call-1',
            }])
        else:
            response = AIMessage(content='These are placeholder results.')
        return ChatResult(generations=[ChatGeneration(message=response)])

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        response = self._generate(messages).generations[0].message
        if response.tool_calls:
            yield ChatGenerationChunk(message=AIMessageChunk(content='', tool_calls=response.tool_calls))
        else:
            for text in ['These are ', 'placeholder results.']:
                yield ChatGenerationChunk(message=AIMessageChunk(content=text))


@pytest.fixture
def configured_agent(monkeypatch):
    def build(selected=('pubmed_search_articles',), call_tool=True):
        model = ToolChatModel(call_tool=call_tool)
        classifier = FakeDecisions(selected)
        settings = lambda: SimpleNamespace(
            openai_api_key=SecretStr('test-key'), decision_model='gpt-6-luna',
            decision_timeout_seconds=30, tool_threshold=0.5,
        )
        monkeypatch.setattr(agent_module, 'Settings', settings)
        monkeypatch.setattr(middleware_module, 'Settings', settings)
        monkeypatch.setattr(agent_module, 'get_llm', lambda settings: model)
        monkeypatch.setattr(middleware_module, 'AsyncOpenAI', lambda **kwargs: classifier)
        return agent_module.build_agent(), model, classifier
    return build


def service_for(monkeypatch, agent):
    monkeypatch.setattr(service_module, 'build_agent', lambda: agent)
    service = ChatService()
    monkeypatch.setattr(resource, 'service', service)
    return service


@pytest.mark.asyncio
async def test_real_agent_executes_selected_tool_and_reuses_scores(configured_agent):
    agent, model, classifier = configured_agent(('pubmed_search_articles', 'clinicaltrials_gov_search_trials'))
    message = 'Find diabetes publications and trials'
    result = await agent.ainvoke({'request': message, 'messages': [{'role': 'user', 'content': message}]})
    assert len(classifier.calls) == 1
    assert classifier.calls[0]['input'] == message
    assert len(classifier.calls[0]['questions']) == 94
    assert all(q['type'] == 'predicate' for q in classifier.calls[0]['questions'])
    assert model.bound_tools == [['clinicaltrials_gov_search_trials', 'pubmed_search_articles']] * 2
    outputs = [m for m in result['messages'] if isinstance(m, ToolMessage)]
    assert len(outputs) == 1
    assert outputs[0].content == 'pubmed_search_articles: static placeholder response.'
    assert result['tool_scores']['pubmed_search_articles'] == 0.5
    assert result['messages'][-1].content == 'These are placeholder results.'


@pytest.mark.asyncio
async def test_service_streams_real_agent_text(configured_agent, monkeypatch):
    agent, model, classifier = configured_agent()
    texts = [text async for text in service_for(monkeypatch, agent).stream('Find publications')]
    assert texts == ['These are ', 'placeholder results.']
    assert len(classifier.calls) == 1
    assert model.bound_tools == [['pubmed_search_articles']] * 2


def test_http_sse_contract(configured_agent, monkeypatch):
    agent, _, _ = configured_agent()
    service_for(monkeypatch, agent)
    with TestClient(app) as client:
        response = client.post('/chat', json={'message': '  Find publications  '})
        assert response.status_code == 200
        assert client.get('/openapi.json').json()['info']['title'] == 'Agent Route'
        assert response.headers['content-type'].startswith('text/event-stream')
        assert response.headers['x-accel-buffering'] == 'no'
        frames = response.text.replace('\r\n', '\n').strip().split('\n\n')
        events = []
        for frame in frames:
            lines = frame.splitlines()
            events.append((lines[0].removeprefix('event: '), json.loads(lines[1].removeprefix('data: '))))
        assert [name for name, data in events] == [
            'response.created', 'response.output_text.delta', 'response.output_text.delta',
            'response.output_text.done', 'response.completed',
        ]
        assert [data for name, data in events] == [
            {'status': 'in_progress'},
            {'delta': 'These are '},
            {'delta': 'placeholder results.'},
            {'text': 'These are placeholder results.'},
            {'status': 'completed'},
        ]
        assert 'text/event-stream' in client.get('/openapi.json').json()['paths']['/chat']['post']['responses']['200']['content']


@pytest.mark.parametrize('payload', [{}, {'message': ''}, {'message': ' \n '},
    {'message': 3}, {'message': 'a' * 20001}, {'message': 'hello', 'extra': True}])
def test_http_rejects_invalid_messages(payload, configured_agent, monkeypatch):
    agent, _, classifier = configured_agent()
    service_for(monkeypatch, agent)
    with TestClient(app) as client:
        assert client.post('/chat', json=payload).status_code == 422
        assert not classifier.calls


@pytest.mark.asyncio
async def test_empty_selection_allows_direct_response(configured_agent, monkeypatch):
    agent, model, _ = configured_agent((), call_tool=False)
    texts = [text async for text in service_for(monkeypatch, agent).stream('Hello')]
    assert model.bound_tools == []
    assert ''.join(texts) == 'These are placeholder results.'


@pytest.mark.asyncio
async def test_concurrent_requests_keep_their_own_tool_selection(monkeypatch):
    class RequestDecisions(FakeDecisions):
        async def create(self, **request):
            classifier = FakeDecisions(('pubmed_search_articles',) if request['input'] == 'papers'
                                        else ('rxnorm_search_drugs',))
            return await classifier.create(**request)

    monkeypatch.setattr(middleware_module, "AsyncOpenAI", lambda **kwargs: RequestDecisions())
    monkeypatch.setattr(middleware_module, "Settings", lambda: SimpleNamespace(
        openai_api_key=SecretStr("test-key"), decision_model="gpt-6-luna",
        decision_timeout_seconds=30, tool_threshold=0.5,
    ))
    async def route(message):
        request = ModelRequest(model=ToolChatModel(call_tool=False), messages=[], tools=HEALTHCARE_TOOLS,
                               state={'request': message, 'messages': []})
        async def handler(overridden):
            await asyncio.sleep(0)
            return ModelResponse(result=[AIMessage(content=','.join(t.name for t in overridden.tools))])
        return await select_tools.awrap_model_call(request, handler)

    paper, drug = await asyncio.gather(route('papers'), route('drugs'))
    assert paper.model_response.result[0].content == 'pubmed_search_articles'
    assert drug.model_response.result[0].content == 'rxnorm_search_drugs'
    assert paper.command.update['tool_scores']['pubmed_search_articles'] == 0.5
    assert drug.command.update['tool_scores']['pubmed_search_articles'] == 0.1


def test_classifier_failure_emits_sse_error_without_calling_model(configured_agent, monkeypatch):
    class FailedDecisions(FakeDecisions):
        async def create(self, **request):
            raise RuntimeError('private upstream failure')

    agent, model, _ = configured_agent()
    monkeypatch.setattr(middleware_module, 'AsyncOpenAI', lambda **kwargs: FailedDecisions())
    service_for(monkeypatch, agent_module.build_agent())
    with TestClient(app) as client:
        response = client.post('/chat', json={'message': 'Find publications'})
    assert 'event: response.failed' in response.text
    assert 'event: response.completed' not in response.text
    assert 'private upstream failure' not in response.text
    assert not model.bound_tools


@pytest.mark.parametrize('endpoint', ['https://example.test/v1', 'https://example.test/v1/chat/completions/'])
def test_navigator_preserves_version_prefix(endpoint):
    settings = Settings(_env_file=None, navigator_api_key='test',
                        navigator_api_endpoint=endpoint, navigator_model='test-model')
    assert get_llm(settings).openai_api_base == 'https://example.test/v1'


def test_all_plugin_operations_have_static_tools():
    expected = json.loads((Path(__file__).parent / 'fixtures/healthcare_tool_names.json').read_text())
    names = [tool.name for tool in HEALTHCARE_TOOLS]
    assert len(names) == len(set(names)) == 94
    assert set(names) == set(expected)
    for tool in HEALTHCARE_TOOLS:
        assert tool.invoke({'query': 'one'}) == tool.invoke({'query': 'two'})
        assert 'static placeholder' in tool.invoke({'query': 'one'})


@pytest.mark.asyncio
async def test_service_only_streams_response_text(monkeypatch):
    class MixedAgent:
        async def astream(self, *args, **kwargs):
            yield AIMessageChunk(content='classifier text'), {'langgraph_node': 'router'}
            yield ToolMessage(content='raw result', tool_call_id='1'), {'langgraph_node': 'tools'}
            yield AIMessageChunk(content=[
                {'type': 'reasoning', 'reasoning': 'hidden reasoning'},
                {'type': 'text', 'text': 'Visible answer'},
            ]), {'langgraph_node': 'model'}
            yield AIMessageChunk(content='', tool_call_chunks=[{
                'name': 'pubmed_search_articles', 'args': '{"query": "secret"}', 'id': '1', 'index': 0,
            }]), {'langgraph_node': 'model'}
    texts = [text async for text in service_for(monkeypatch, MixedAgent()).stream('hello')]
    assert texts == ['Visible answer']


@pytest.mark.asyncio
async def test_http_disconnect_cancels_underlying_agent(monkeypatch):
    disconnected = asyncio.Event()
    closed = asyncio.Event()
    sent = []

    class BlockingAgent:
        async def astream(self, *args, **kwargs):
            try:
                yield AIMessageChunk(content='first'), {'langgraph_node': 'model'}
                await asyncio.Event().wait()
            finally:
                closed.set()

    service_for(monkeypatch, BlockingAgent())
    request_sent = False
    async def receive():
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {'type': 'http.request', 'body': json.dumps({'message': 'hello'}).encode(), 'more_body': False}
        await disconnected.wait()
        return {'type': 'http.disconnect'}
    async def send(event):
        sent.append(event)
        if b'event: response.output_text.delta' in event.get('body', b''):
            disconnected.set()

    async with app.router.lifespan_context(app):
        await asyncio.wait_for(app({
            'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.3'},
            'http_version': '1.1', 'method': 'POST', 'scheme': 'http',
            'path': '/chat', 'raw_path': b'/chat', 'query_string': b'',
            'headers': [(b'content-type', b'application/json')],
            'client': ('127.0.0.1', 1234), 'server': ('test', 80),
        }, receive, send), timeout=3)
    assert closed.is_set()
    assert not any(b'event: response.completed' in event.get('body', b'') for event in sent)


def test_blank_openai_key_allows_app_but_blocks_routing(configured_agent, monkeypatch):
    agent, model, decisions = configured_agent()
    original_settings = middleware_module.Settings
    def blank_settings():
        settings = original_settings()
        settings.openai_api_key = SecretStr('')
        return settings
    monkeypatch.setattr(middleware_module, 'Settings', blank_settings)
    service_for(monkeypatch, agent)
    with TestClient(app) as client:
        assert client.get('/openapi.json').status_code == 200
        response = client.post('/chat', json={'message': 'Find publications'})
    assert 'event: response.failed' in response.text
    assert not decisions.calls
    assert not model.bound_tools


@pytest.mark.parametrize('invalid', ['refusal', 'missing', 'duplicate', 'unknown', 'nan', 'out_of_range'])
def test_invalid_decision_answers_stop_routing(invalid):
    answers = [SimpleNamespace(type='predicate', name=q['name'], probability=0.5)
               for q in middleware_module.QUESTIONS]
    if invalid == 'refusal':
        answers[0] = SimpleNamespace(type='refusal', name=answers[0].name)
    elif invalid == 'missing':
        answers.pop()
    elif invalid == 'duplicate':
        answers.append(answers[0])
    elif invalid == 'unknown':
        answers[0].name = 'unknown'
    elif invalid == 'nan':
        answers[0].probability = float('nan')
    else:
        answers[0].probability = 1.1
    with pytest.raises(ValueError):
        middleware_module.predicate_scores(answers)


@pytest.mark.asyncio
async def test_real_openai_sdk_decisions_contract(configured_agent, monkeypatch):
    import httpx2
    from openai import AsyncOpenAI

    agent, model, _ = configured_agent()
    requests = []
    async def respond(request):
        assert request.method == 'POST'
        assert str(request.url) == 'https://api.openai.com/v1/decisions'
        body = json.loads(request.content)
        requests.append(body)
        assert body['model'] == 'gpt-6-luna'
        assert body['input'] == 'Find publications'
        assert len(body['questions']) == 94
        assert all(q['type'] == 'predicate' for q in body['questions'])
        # Use reversed answers to prove matching is by name, not position.
        return httpx2.Response(200, json={
            'model': body['model'],
            'answers': [{'type': 'predicate', 'name': q['name'],
                         'probability': 0.9 if q['name'] == 'pubmed_search_articles' else 0.1}
                        for q in reversed(body['questions'])],
            'usage': {'input_tokens': 1, 'output_tokens': 0, 'total_tokens': 1,
                      'input_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0},
                      'output_tokens_details': {'reasoning_tokens': 0}},
        })

    client = AsyncOpenAI(api_key='test-key', base_url='https://api.openai.com/v1',
                         http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond)))
    monkeypatch.setattr(middleware_module, 'AsyncOpenAI', lambda **kwargs: client)
    result = await agent.ainvoke({'request': 'Find publications',
                                 'messages': [{'role': 'user', 'content': 'Find publications'}]})
    assert len(requests) == 1
    assert model.bound_tools == [['pubmed_search_articles']] * 2
    assert result['tool_scores']['pubmed_search_articles'] == 0.9
    assert client.is_closed()


def test_resource_owns_one_service_with_independent_request_state(configured_agent, monkeypatch):
    from src.resource import resource

    agent, _, decisions = configured_agent()
    service_for(monkeypatch, agent)
    with TestClient(app) as client:
        service = resource.service
        assert not hasattr(app.state, 'chat_service')
        first = client.post('/chat', json={'message': 'Find publications'})
        second = client.post('/chat', json={'message': 'Find other publications'})
        assert resource.service is service
        assert 'event: response.completed' in first.text
        assert 'event: response.completed' in second.text
    assert len(decisions.calls) == 2
    assert [call['input'] for call in decisions.calls] == ['Find publications', 'Find other publications']
