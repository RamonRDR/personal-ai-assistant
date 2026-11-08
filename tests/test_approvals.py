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
