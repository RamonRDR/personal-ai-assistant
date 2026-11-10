"""Human-in-the-loop is an enforced transactional boundary."""

from datetime import timedelta

from personal_ai_assistant.db import to_iso, utcnow
from personal_ai_assistant.models import Approval


def create(client):
    return client.post("/api/tasks", json={"title": "Keep me safe"}).json()["data"]["id"]


def request_delete(client, identifier):
    result = client.delete(f"/api/tasks/{identifier}").json()
    assert result["status"] == "approval_required"
    assert result["proposed_changes"] == {"task_id": identifier}
    assert client.get(f"/api/tasks/{identifier}").status_code == 200
    return result


def decide(client, item, action="approve", token=None):
    return client.post(
        f"/api/approvals/{item['approval_id']}/{action}",
        json={"confirmation_token": token or item["confirmation_token"]},
    )


def test_approve_executes_once(client):
    identifier = create(client)
    item = request_delete(client, identifier)
    assert decide(client, item).json()["status"] == "success"
    assert client.get(f"/api/tasks/{identifier}").status_code == 404
    assert decide(client, item).status_code == 409


def test_reject_does_not_execute(client):
    identifier = create(client)
    item = request_delete(client, identifier)
    assert decide(client, item, "reject").json()["status"] == "rejected"
    assert client.get(f"/api/tasks/{identifier}").status_code == 200
    assert decide(client, item).status_code == 409


def test_wrong_confirmation_does_not_consume_approval(client):
    identifier = create(client)
    item = request_delete(client, identifier)
    assert decide(client, item, token="wrong_token_of_sufficient_length").status_code == 403
    assert client.get(f"/api/tasks/{identifier}").status_code == 200
    assert decide(client, item).json()["status"] == "success"


def test_expiration_blocks_execution(client, db):
    identifier = create(client)
    item = request_delete(client, identifier)
    record = db.get(Approval, item["approval_id"])
    record.expires_at = to_iso(utcnow() - timedelta(seconds=5))
    db.commit()
    assert decide(client, item).status_code == 410
    assert client.get(f"/api/tasks/{identifier}").status_code == 200
    assert decide(client, item).status_code == 409


def test_update_requires_approval(client):
    identifier = create(client)
    result = client.patch(f"/api/tasks/{identifier}", json={"title": "Changed"}).json()
    assert result["status"] == "approval_required"
    assert client.get(f"/api/tasks/{identifier}").json()["title"] == "Keep me safe"
    assert decide(client, result).json()["status"] == "success"
    assert client.get(f"/api/tasks/{identifier}").json()["title"] == "Changed"


def test_event_delete_requires_approval(client):
    event = client.post(
        "/api/events",
        json={
            "title": "Coffee",
            "start_at": "2026-11-08T12:00:00+00:00",
            "end_at": "2026-11-08T13:00:00+00:00",
            "timezone": "UTC",
        },
    ).json()["data"]
    result = client.delete(f"/api/events/{event['id']}").json()
    assert result["status"] == "approval_required"
    assert len(client.get("/api/events").json()) == 1
    assert decide(client, result).json()["status"] == "success"
    assert len(client.get("/api/events").json()) == 0


def test_approval_token_is_not_in_list(client):
    identifier = create(client)
    item = request_delete(client, identifier)
    listed = client.get("/api/approvals").json()
    assert listed[0]["approval_id"] == item["approval_id"]
    assert "confirmation_token" not in listed[0]


def test_stale_task_approval_cannot_delete_reused_id(client):
    original = create(client)
    first = request_delete(client, original)
    second = request_delete(client, original)
    assert decide(client, first).json()["status"] == "success"
    replacement = client.post("/api/tasks", json={"title": "Replacement"}).json()["data"]
    assert replacement["id"] == original
    stale = decide(client, second).json()
    assert stale["status"] == "error"
    assert "target changed" in stale["error"].lower()
    assert client.get(f"/api/tasks/{original}").json()["title"] == "Replacement"
    assert decide(client, second).status_code == 409


def test_stale_task_approval_cannot_edit_reused_id(client):
    original = create(client)
    proposal = client.patch(f"/api/tasks/{original}", json={"title": "Unauthorized"}).json()
    deletion = request_delete(client, original)
    assert decide(client, deletion).json()["status"] == "success"
    replacement = client.post("/api/tasks", json={"title": "Fresh"}).json()["data"]
    assert replacement["id"] == original
    assert decide(client, proposal).json()["status"] == "error"
    assert client.get(f"/api/tasks/{original}").json()["title"] == "Fresh"


def test_stale_event_approval_cannot_delete_reused_id(client):
    payload = {
        "title": "Original",
        "start_at": "2026-11-08T12:00:00+00:00",
        "end_at": "2026-11-08T13:00:00+00:00",
        "timezone": "UTC",
    }
    original = client.post("/api/events", json=payload).json()["data"]["id"]
    first = client.delete(f"/api/events/{original}").json()
    second = client.delete(f"/api/events/{original}").json()
    assert decide(client, first).json()["status"] == "success"
    replacement = client.post("/api/events", json={**payload, "title": "Fresh"}).json()["data"]
    assert replacement["id"] == original
    assert decide(client, second).json()["status"] == "error"
    assert client.get("/api/events").json()[0]["title"] == "Fresh"


def test_approved_task_deletion_unlinks_reminders_without_losing_them(client):
    task = create(client)
    reminder = client.post(
        "/api/reminders",
        json={
            "message": "Keep my reminder",
            "task_id": task,
            "scheduled_at": "2026-11-08T15:00:00+00:00",
        },
    ).json()["data"]
    proposal = request_delete(client, task)
    result = decide(client, proposal).json()
    assert result["status"] == "success"
    assert result["data"]["detached_reminders"] == 1
    retained = client.get("/api/reminders?pending_only=false").json()
    assert len(retained) == 1
    assert retained[0]["id"] == reminder["id"]
    assert retained[0]["task_id"] is None
    assert retained[0]["message"] == "Keep my reminder"


def test_approved_event_deletion_unlinks_reminders(client):
    event = client.post(
        "/api/events",
        json={
            "title": "Meeting",
            "start_at": "2026-11-08T12:00:00+00:00",
            "end_at": "2026-11-08T13:00:00+00:00",
            "timezone": "UTC",
        },
    ).json()["data"]["id"]
    reminder = client.post(
        "/api/reminders",
        json={
            "message": "Keep event reminder",
            "event_id": event,
            "scheduled_at": "2026-11-08T11:00:00+00:00",
        },
    ).json()["data"]
    proposal = client.delete(f"/api/events/{event}").json()
    assert decide(client, proposal).json()["data"]["detached_reminders"] == 1
    retained = client.get("/api/reminders?pending_only=false").json()
    assert retained[0]["id"] == reminder["id"]
    assert retained[0]["event_id"] is None


def test_legacy_unbound_approval_cannot_mutate_task(client, db):
    task = create(client)
    proposal = request_delete(client, task)
    record = db.get(Approval, proposal["approval_id"])
    record.resource_identity = None
    db.commit()
    result = decide(client, proposal).json()
    assert result["status"] == "error"
    assert client.get(f"/api/tasks/{task}").status_code == 200
