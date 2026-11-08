"""The real model adapter is tested with a fake network provider, never paid API."""

import json

import httpx

from personal_ai_assistant.assistant import respond
from personal_ai_assistant.config import settings
from personal_ai_assistant.models import Task


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.posts = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def post(self, url, **kwargs):
        self.posts.append({"url": url, **kwargs})
        return FakeResponse(next(self.responses))


def tool_call(name, arguments, call_id="tool_1"):
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


def provider_message(*, calls=None, content=None, tokens=3):
    return {
        "choices": [{"message": {"content": content, "tool_calls": calls or []}}],
        "usage": {"total_tokens": tokens},
    }


def enable_fake_provider(monkeypatch, responses):
    provider = FakeProvider(responses)
    monkeypatch.setattr(settings, "mode", "openai_compatible")
    monkeypatch.setattr(settings, "llm_api_key", "synthetic-test-key")
    monkeypatch.setattr(httpx, "Client", lambda **_: provider)
    return provider


def test_llm_tool_call_persists_real_task(db, monkeypatch):
    provider = enable_fake_provider(
        monkeypatch,
        [
            provider_message(calls=[tool_call("create_task", {"title": "From fake LLM"})]),
            provider_message(content="Task completed", tokens=5),
        ],
    )
    result = respond(db, "Please create a task")
    assert result["status"] == "completed"
    assert result["tool_results"][0]["status"] == "success"
    assert result["reply"] == "Verified tool outcomes: create_task: success"
    assert result["usage"]["total_tokens"] == 8
    assert db.query(Task).one().title == "From fake LLM"
    assert len(provider.posts) == 2
    assert provider.posts[0]["json"]["tool_choice"] == "auto"


def test_llm_cannot_approve_a_sensitive_action(db, monkeypatch):
    created = Task(title="Protected")
    db.add(created)
    db.commit()
    provider = enable_fake_provider(
        monkeypatch,
        [
            provider_message(calls=[tool_call("delete_task", {"task_id": created.id})]),
            provider_message(content="Deleted"),
        ],
    )
    result = respond(db, "Delete that task")
    assert result["tool_results"][0]["status"] == "approval_required"
    assert result["reply"] == "Verified tool outcomes: delete_task: approval_required"
    assert db.get(Task, created.id) is not None
    second_request = json.dumps(provider.posts[1]["json"])
    assert "confirmation_token" not in second_request


def test_llm_wrong_tool_never_executes(db, monkeypatch):
    enable_fake_provider(
        monkeypatch,
        [
            provider_message(calls=[tool_call("execute_shell", {"cmd": "id"})]),
            provider_message(content="Done"),
        ],
    )
    result = respond(db, "Execute a command")
    assert result["tool_results"][0]["status"] == "error"
    assert db.query(Task).count() == 0


def test_llm_tool_call_limit_is_enforced(db, monkeypatch):
    monkeypatch.setattr(settings, "max_tool_calls", 1)
    enable_fake_provider(
        monkeypatch,
        [provider_message(calls=[
            tool_call("create_task", {"title": "First"}, "one"),
            tool_call("create_task", {"title": "Second"}, "two"),
        ])],
    )
    result = respond(db, "Create multiple tasks")
    assert result["status"] == "limit_reached"
    assert db.query(Task).count() == 1


def test_llm_network_failure_is_explicit(db, monkeypatch):
    monkeypatch.setattr(settings, "mode", "openai_compatible")
    monkeypatch.setattr(settings, "llm_api_key", "synthetic-test-key")

    class OfflineClient:
        def __init__(self, **_):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def post(self, *_args, **_kwargs):
            raise httpx.ConnectError("synthetic provider offline")

    monkeypatch.setattr(httpx, "Client", OfflineClient)
    result = respond(db, "create task")
    assert result["status"] == "unavailable"
    assert db.query(Task).count() == 0
