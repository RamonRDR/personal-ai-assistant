"""Deterministic business rules. None of these functions invoke a model."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from personal_ai_assistant.db import from_iso, to_iso, utcnow
from personal_ai_assistant.models import Event, Reminder, Task
from personal_ai_assistant.schemas import EventCreate, EventUpdate, ReminderCreate, TaskCreate, TaskUpdate


def not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource} not found")


def as_dict(obj) -> dict:
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


def create_task(db: Session, data: TaskCreate) -> dict:
    task = Task(**{**data.model_dump(exclude={"due_at"}), "due_at": to_iso(data.due_at) if data.due_at else None})
    db.add(task)
    db.flush()
    return as_dict(task)


def get_task(db: Session, task_id: int) -> dict:
    item = db.get(Task, task_id)
    if item is None:
        raise not_found("Task")
    return as_dict(item)


def list_tasks(db: Session, status: str | None = None) -> list[dict]:
    query = select(Task).order_by(Task.id.desc())
    if status:
        query = query.where(Task.status == status)
    return [as_dict(item) for item in db.scalars(query).all()]


def update_task(db: Session, task_id: int, data: TaskUpdate) -> dict:
    item = db.get(Task, task_id)
    if item is None:
        raise not_found("Task")
    changes = data.model_dump(exclude_unset=True)
    for key, value in changes.items():
        if key == "due_at":
            value = to_iso(value) if value is not None else None
        if value is None and key != "due_at":
            raise HTTPException(422, detail=f"{key} cannot be null")
        setattr(item, key, value)
    item.updated_at = to_iso(utcnow())
    db.flush()
    return as_dict(item)


def complete_task(db: Session, task_id: int) -> dict:
    return update_task(db, task_id, TaskUpdate(status="completed"))


def delete_task(db: Session, task_id: int) -> dict:
    item = db.get(Task, task_id)
    if item is None:
        raise not_found("Task")
    if db.scalar(select(Reminder.id).where(Reminder.task_id == task_id).limit(1)):
        raise HTTPException(409, detail="Delete linked reminders first")
    db.delete(item)
    db.flush()
    return {"deleted": True, "task_id": task_id}


def create_event(db: Session, data: EventCreate) -> dict:
    fields = data.model_dump(exclude={"start_at", "end_at"})
    item = Event(**fields, start_at=to_iso(data.start_at), end_at=to_iso(data.end_at))
    db.add(item)
    db.flush()
    return as_dict(item)


def list_events(db: Session) -> list[dict]:
    return [as_dict(item) for item in db.scalars(select(Event).order_by(Event.start_at)).all()]


def update_event(db: Session, event_id: int, data: EventUpdate) -> dict:
    item = db.get(Event, event_id)
    if item is None:
        raise not_found("Event")
    updates = data.model_dump(exclude_unset=True)
    present = as_dict(item)
    for key, value in updates.items():
        if value is None and key != "location":
            raise HTTPException(422, detail=f"{key} cannot be null")
        present[key] = value
    # Revalidate the entire combined event, including timezone and DST offsets.
    event = EventCreate.model_validate({
        "title": present["title"],
        "description": present["description"],
        "start_at": present["start_at"],
        "end_at": present["end_at"],
        "timezone": present["timezone"],
        "location": present["location"],
    })
    for key, value in updates.items():
        if key in ("start_at", "end_at"):
            value = to_iso(value)
        setattr(item, key, value)
    # The event validator above is the authority on schedule integrity.
    _ = event
    db.flush()
    return as_dict(item)


def delete_event(db: Session, event_id: int) -> dict:
    item = db.get(Event, event_id)
    if item is None:
        raise not_found("Event")
    if db.scalar(select(Reminder.id).where(Reminder.event_id == event_id).limit(1)):
        raise HTTPException(409, detail="Delete linked reminders first")
    db.delete(item)
    db.flush()
    return {"deleted": True, "event_id": event_id}


def create_reminder(db: Session, data: ReminderCreate) -> dict:
    if data.task_id and not db.get(Task, data.task_id):
        raise not_found("Task")
    if data.event_id and not db.get(Event, data.event_id):
        raise not_found("Event")
    reminder = Reminder(
        message=data.message, scheduled_at=to_iso(data.scheduled_at),
        task_id=data.task_id, event_id=data.event_id
    )
    db.add(reminder)
    db.flush()
    return as_dict(reminder)


def list_reminders(db: Session, pending_only: bool = True) -> list[dict]:
    query = select(Reminder).order_by(Reminder.scheduled_at)
    if pending_only:
        query = query.where(Reminder.delivered_at.is_(None))
    return [as_dict(item) for item in db.scalars(query).all()]


def deliver_reminder(db: Session, reminder_id: int) -> dict:
    stamp = to_iso(utcnow())
    result = db.execute(
        update(Reminder)
        .where(Reminder.id == reminder_id, Reminder.delivered_at.is_(None))
        .values(delivered_at=stamp)
    )
    if result.rowcount != 1:
        if db.get(Reminder, reminder_id) is None:
            raise not_found("Reminder")
        raise HTTPException(409, detail="Reminder already delivered")
    db.flush()
    return as_dict(db.get(Reminder, reminder_id))


def daily_summary(db: Session, day: date, timezone: str = "UTC") -> dict:
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise HTTPException(422, detail="Invalid IANA timezone") from exc
    start = datetime.combine(day, time.min, tzinfo=zone).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone).astimezone(UTC)
    a, b = to_iso(start), to_iso(end)
    tasks = [
        as_dict(x) for x in db.scalars(
            select(Task).where(Task.due_at >= a, Task.due_at < b).order_by(Task.due_at)
        ).all()
    ]
    events = [
        as_dict(x) for x in db.scalars(
            select(Event).where(Event.start_at >= a, Event.start_at < b).order_by(Event.start_at)
        ).all()
    ]
    reminders = [
        as_dict(x) for x in db.scalars(
            select(Reminder).where(
                Reminder.scheduled_at >= a, Reminder.scheduled_at < b,
                Reminder.delivered_at.is_(None),
            ).order_by(Reminder.scheduled_at)
        ).all()
    ]
    return {"day": day.isoformat(), "timezone": timezone, "tasks": tasks,
            "events": events, "reminders": reminders, "counts": {
                "tasks": len(tasks), "events": len(events), "reminders": len(reminders)
            }}
