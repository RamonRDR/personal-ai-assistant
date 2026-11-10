"""Loopback-only REST API and the browser demo. No public unauthenticated deployment."""

from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from personal_ai_assistant import services
from personal_ai_assistant.assistant import respond
from personal_ai_assistant.config import settings
from personal_ai_assistant.db import get_db
from personal_ai_assistant.models import Approval, Message, ToolExecution
from personal_ai_assistant.schemas import (
    ApprovalDecision,
    ChatInput,
    EventCreate,
    EventUpdate,
    ReminderCreate,
    TaskCreate,
    TaskUpdate,
)
from personal_ai_assistant.tools import manager, public_catalog

Db = Annotated[Session, Depends(get_db)]
app = FastAPI(
    title="Personal AI Assistant",
    version="0.1.0",
    description="Local-only task assistant with real tools and human approval.",
)


LOCAL_HOSTS = {
    "127.0.0.1", "127.0.0.1:8000",
    "localhost", "localhost:8000",
    "[::1]", "[::1]:8000",
}


@app.middleware("http")
async def restrict_to_loopback(request: Request, call_next):
    client = request.client.host if request.client else ""
    # Check both the socket peer and Host to resist DNS rebinding.
    if client not in ("127.0.0.1", "::1", "localhost", "testclient"):
        return JSONResponse(status_code=403, content={"detail": "Local connections only"})
    host = request.headers.get("host", "")
    if host not in LOCAL_HOSTS and not (client == "testclient" and host == "testserver"):
        return JSONResponse(status_code=403, content={"detail": "Untrusted Host header"})

    # Block cross-site Origin/Referer/Fetch Metadata, including read requests.
    expected_origin = "http://" + host
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    fetch_site = request.headers.get("sec-fetch-site")
    if (
        (origin is not None and origin != expected_origin)
        or (
            referer is not None
            and urlsplit(referer).scheme + "://" + urlsplit(referer).netloc != expected_origin
        )
        or fetch_site in ("cross-site", "same-site")
    ):
        return JSONResponse(status_code=403, content={"detail": "Cross-origin request blocked"})

    # This non-simple header requires a CORS preflight for hostile browser
    # mutations, including bodyless POST. No permissive CORS is configured.
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        if request.headers.get("x-local-request") != "1":
            return JSONResponse(status_code=403, content={"detail": "Local request header required"})
    return await call_next(request)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(
        Path(__file__).parent / "static" / "index.html", headers={"Cache-Control": "no-store"}
    )


@app.get("/health")
def health():
    return {"status": "ok", "mode": settings.mode, "scope": "local-only"}


@app.get("/api/tools")
def tools_catalog():
    return {"tools": public_catalog()}


@app.get("/api/tasks")
def tasks(db: Db, status: str | None = None):
    if status not in (None, "pending", "completed"):
        raise HTTPException(422, detail="Invalid task status")
    return services.list_tasks(db, status)


@app.post("/api/tasks", status_code=201)
def create_task(data: TaskCreate, db: Db):
    outcome = manager.invoke(db, "create_task", data.model_dump(mode="json"))
    return outcome


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int, db: Db):
    return services.get_task(db, task_id)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Db):
    return manager.invoke(
        db,
        "update_task",
        {"task_id": task_id, "patch": data.model_dump(exclude_unset=True, mode="json")},
    )


@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Db):
    return manager.invoke(db, "complete_task", {"task_id": task_id})


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Db):
    return manager.invoke(db, "delete_task", {"task_id": task_id})


@app.get("/api/events")
def events(db: Db):
    return services.list_events(db)


@app.post("/api/events", status_code=201)
def create_event(data: EventCreate, db: Db):
    return manager.invoke(db, "create_event", data.model_dump(mode="json"))


@app.patch("/api/events/{event_id}")
def update_event(event_id: int, data: EventUpdate, db: Db):
    return manager.invoke(
        db,
        "update_event",
        {"event_id": event_id, "patch": data.model_dump(exclude_unset=True, mode="json")},
    )


@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Db):
    return manager.invoke(db, "delete_event", {"event_id": event_id})


@app.get("/api/reminders")
def reminders(db: Db, pending_only: bool = True):
    return services.list_reminders(db, pending_only)


@app.post("/api/reminders", status_code=201)
def create_reminder(data: ReminderCreate, db: Db):
    return manager.invoke(db, "create_reminder", data.model_dump(mode="json"))


@app.post("/api/reminders/{reminder_id}/deliver")
def deliver_reminder(reminder_id: int, db: Db):
    return manager.invoke(db, "deliver_reminder", {"reminder_id": reminder_id})


@app.get("/api/summary")
def summary(db: Db, day: Annotated[date, Query()], timezone: str = "UTC"):
    return services.daily_summary(db, day, timezone)


@app.post("/api/chat")
def chat(data: ChatInput, db: Db):
    return respond(db, data.message)


@app.get("/api/history")
def history(db: Db):
    rows = db.scalars(
        select(Message).order_by(Message.id.desc()).limit(settings.history_limit)
    ).all()
    return [
        {"role": x.role, "content": x.content, "created_at": x.created_at} for x in reversed(rows)
    ]


@app.get("/api/approvals")
def pending_approvals(db: Db):
    # Tokens are only returned once, directly to the proposing user, never from a list.
    rows = db.scalars(select(Approval).where(Approval.status == "pending")).all()
    return [
        {
            "approval_id": x.id,
            "tool_name": x.tool_name,
            "status": x.status,
            "expires_at": x.expires_at,
        }
        for x in rows
    ]


@app.post("/api/approvals/{approval_id}/approve")
def approve(approval_id: str, data: ApprovalDecision, db: Db):
    return manager.decide(db, approval_id, data.confirmation_token, approve=True)


@app.post("/api/approvals/{approval_id}/reject")
def reject(approval_id: str, data: ApprovalDecision, db: Db):
    return manager.decide(db, approval_id, data.confirmation_token, approve=False)


@app.get("/api/audit")
def audit(db: Db):
    rows = db.scalars(select(ToolExecution).order_by(ToolExecution.id.desc()).limit(50)).all()
    return [
        {"tool": x.name, "outcome": x.outcome, "time": x.created_at, "approval_id": x.approval_id}
        for x in rows
    ]
