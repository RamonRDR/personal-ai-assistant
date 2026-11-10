"""Local-only persistence. All timestamps are canonical UTC ISO-8601 text."""

from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from personal_ai_assistant.db import Base, to_iso, utcnow


def timestamp() -> str:
    return to_iso(utcnow())


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_identity: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    due_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)
    updated_at: Mapped[str] = mapped_column(String(40), default=timestamp)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_identity: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    start_at: Mapped[str] = mapped_column(String(40))
    end_at: Mapped[str] = mapped_column(String(40))
    timezone: Mapped[str] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(String(500))
    scheduled_at: Mapped[str] = mapped_column(String(40))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    delivered_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tool_name: Mapped[str] = mapped_column(String(80))
    arguments_json: Mapped[str] = mapped_column(Text)
    token_hash: Mapped[str] = mapped_column(String(64))
    # Old proposals without a resource binding fail closed on approval.
    resource_identity: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    expires_at: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)
    decided_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    outcome: Mapped[str] = mapped_column(String(40))
    approval_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(12))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=timestamp)
