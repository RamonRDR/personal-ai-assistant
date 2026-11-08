"""Explicit allowlisted tools. There is no shell, file or arbitrary HTTP tool."""

import hashlib
import hmac
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import update
from sqlalchemy.orm import Session

from personal_ai_assistant import services
from personal_ai_assistant.config import settings
from personal_ai_assistant.db import from_iso, to_iso, utcnow
from personal_ai_assistant.models import Approval, ToolExecution
from personal_ai_assistant.schemas import (
    DaySummary,
    EventCreate,
    EventId,
    EventUpdate,
    ReminderCreate,
    ReminderId,
    StrictModel,
    TaskCreate,
    TaskId,
    TaskList,
    TaskUpdate,
)


class Empty(StrictModel):
    pass


class TaskPatch(StrictModel):
    task_id: int = Field(gt=0)
    patch: TaskUpdate


class EventPatch(StrictModel):
    event_id: int = Field(gt=0)
    patch: EventUpdate


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: type[BaseModel]
    risk: str
    handler: Callable[[Session, Any], Any]


TOOL_SPECS = (
    ToolSpec(
        "create_task",
        "Create a local task",
        TaskCreate,
        "write",
        lambda db, a: services.create_task(db, a),
    ),
    ToolSpec(
        "list_tasks",
        "List local tasks",
        TaskList,
        "read",
        lambda db, a: services.list_tasks(db, a.status),
    ),
    ToolSpec(
        "get_task",
        "Get a task by its ID",
        TaskId,
        "read",
        lambda db, a: services.get_task(db, a.task_id),
    ),
    ToolSpec(
        "update_task",
        "Edit a task; needs human confirmation",
        TaskPatch,
        "sensitive",
        lambda db, a: services.update_task(db, a.task_id, a.patch),
    ),
    ToolSpec(
        "complete_task",
        "Complete a local task",
        TaskId,
        "write",
        lambda db, a: services.complete_task(db, a.task_id),
    ),
    ToolSpec(
        "delete_task",
        "Delete a task; needs human confirmation",
        TaskId,
        "sensitive",
        lambda db, a: services.delete_task(db, a.task_id),
    ),
    ToolSpec(
        "create_event",
        "Create a calendar event in the local database",
        EventCreate,
        "write",
        lambda db, a: services.create_event(db, a),
    ),
    ToolSpec(
        "list_events", "List local events", Empty, "read", lambda db, a: services.list_events(db)
    ),
    ToolSpec(
        "update_event",
        "Edit an event; needs human confirmation",
        EventPatch,
        "sensitive",
        lambda db, a: services.update_event(db, a.event_id, a.patch),
    ),
    ToolSpec(
        "delete_event",
        "Delete an event; needs human confirmation",
        EventId,
        "sensitive",
        lambda db, a: services.delete_event(db, a.event_id),
    ),
    ToolSpec(
        "get_daily_summary",
        "Summarize local tasks, reminders and events for a day",
        DaySummary,
        "read",
        lambda db, a: services.daily_summary(db, a.day, a.timezone),
    ),
    ToolSpec(
        "create_reminder",
        "Schedule a local reminder; no external delivery",
        ReminderCreate,
        "write",
        lambda db, a: services.create_reminder(db, a),
    ),
    ToolSpec(
        "list_reminders",
        "List pending local reminders",
        Empty,
        "read",
        lambda db, a: services.list_reminders(db),
    ),
    ToolSpec(
        "deliver_reminder",
        "Mark a reminder as delivered locally",
        ReminderId,
        "write",
        lambda db, a: services.deliver_reminder(db, a.reminder_id),
    ),
)
REGISTRY = {spec.name: spec for spec in TOOL_SPECS}


def public_catalog() -> list[dict]:
    return [
        {
            "name": t.name,
            "description": t.description,
            "risk": t.risk,
            "input_schema": t.schema.model_json_schema(),
        }
        for t in TOOL_SPECS
    ]


def llm_catalog() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema.model_json_schema(),
            },
        }
        for t in TOOL_SPECS
    ]


def execution_log(db: Session, name: str, outcome: str, approval_id: str | None = None):
    db.add(ToolExecution(name=name, outcome=outcome, approval_id=approval_id))


class ToolManager:
    def invoke(
        self,
        db: Session,
        name: str,
        arguments: dict,
        *,
        approved: bool = False,
        approval_id: str | None = None,
    ) -> dict:
        spec = REGISTRY.get(name)
        if spec is None:
            execution_log(db, name[:80], "unknown_tool")
            db.commit()
            return {"status": "error", "error": "Unknown or prohibited tool"}
        try:
            parsed = spec.schema.model_validate(arguments)
        except ValidationError:
            execution_log(db, name, "invalid_arguments")
            db.commit()
            return {"status": "error", "error": "Invalid tool arguments"}
        if spec.risk == "sensitive" and not approved:
            token = secrets.token_urlsafe(32)
            approval = Approval(
                id=str(uuid4()),
                tool_name=name,
                arguments_json=parsed.model_dump_json(),
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                status="pending",
                expires_at=to_iso(utcnow() + timedelta(seconds=settings.approval_ttl_seconds)),
            )
            db.add(approval)
            execution_log(db, name, "approval_required", approval.id)
            db.commit()
            return {
                "status": "approval_required",
                "approval_id": approval.id,
                "confirmation_token": token,
                "proposed_action": name,
                "proposed_changes": parsed.model_dump(mode="json"),
                "expires_at": approval.expires_at,
            }
        try:
            data = spec.handler(db, parsed)
            execution_log(db, name, "success", approval_id)
            db.commit()
            return {"status": "success", "tool": name, "data": data}
        except (HTTPException, ValueError) as exc:
            db.rollback()
            execution_log(db, name, "failed", approval_id)
            db.commit()
            return {
                "status": "error",
                "tool": name,
                "error": exc.detail if isinstance(exc, HTTPException) else "Invalid operation",
            }
        except Exception:
            db.rollback()
            execution_log(db, name, "failed", approval_id)
            db.commit()
            return {"status": "error", "tool": name, "error": "Tool execution failed"}

    def decide(self, db: Session, approval_id: str, token: str, *, approve: bool) -> dict:
        approval = db.get(Approval, approval_id)
        if approval is None:
            raise HTTPException(404, detail="Approval not found")
        if not hmac.compare_digest(approval.token_hash, hashlib.sha256(token.encode()).hexdigest()):
            raise HTTPException(403, detail="Invalid confirmation token")
        if approval.status != "pending":
            raise HTTPException(409, detail="Approval already consumed")
        if from_iso(approval.expires_at) <= utcnow():
            db.execute(
                update(Approval)
                .where(Approval.id == approval_id, Approval.status == "pending")
                .values(status="expired", decided_at=to_iso(utcnow()))
            )
            db.commit()
            raise HTTPException(410, detail="Approval expired")
        status = "processing" if approve else "rejected"
        claimed = db.execute(
            update(Approval)
            .where(Approval.id == approval_id, Approval.status == "pending")
            .values(status=status, decided_at=to_iso(utcnow()))
        )
        if claimed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, detail="Approval already consumed")
        name, arguments = approval.tool_name, json.loads(approval.arguments_json)
        # Commit the single-use claim before running any operation.
        db.commit()
        if not approve:
            execution_log(db, name, "rejected", approval_id)
            db.commit()
            return {"status": "rejected", "approval_id": approval_id}
        result = self.invoke(db, name, arguments, approved=True, approval_id=approval_id)
        db.execute(
            update(Approval)
            .where(Approval.id == approval_id)
            .values(status="executed" if result["status"] == "success" else "failed")
        )
        db.commit()
        return {"approval_id": approval_id, **result}


manager = ToolManager()
