"""Deterministic command grammar and optional adapter failure handling."""

from personal_ai_assistant.assistant import parse_demo, respond
from personal_ai_assistant.config import settings
from personal_ai_assistant.tools import manager


def test_demo_grammar():
    assert parse_demo("create task: Write docs") == ("create_task", {"title": "Write docs"})
    assert parse_demo("update task: 3 | Revised") == (
        "update_task", {"task_id": 3, "patch": {"title": "Revised"}}
    )
    assert parse_demo("Hello, world") is None
    assert parse_demo("create event: Demo | 2026-11-08T10:00:00+00:00 | "
                      "2026-11-08T11:00:00+00:00 | UTC")[0] == "create_event"


def test_demo_error_not_success(db):
    result = respond(db, "complete task: 999")
    assert result["status"] == "error"
    assert "could not" in result["reply"]


def test_no_paid_provider_call_without_key(db, monkeypatch):
    monkeypatch.setattr(settings, "mode", "openai_compatible")
    monkeypatch.setattr(settings, "llm_api_key", None)
    result = respond(db, "create task please")
    assert result["status"] == "unavailable"
    assert "no paid API call" in result["reply"]


def test_call_limit_config_is_bounded():
    assert settings.max_tool_calls <= 8


def test_no_tool_can_approve_itself():
    from personal_ai_assistant.tools import REGISTRY
    assert all("approve" not in key and "shell" not in key for key in REGISTRY)
