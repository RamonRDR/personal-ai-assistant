"""Bounded schemas for all public mutations and tool arguments."""

from datetime import date
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Title = Annotated[str, Field(min_length=1, max_length=200)]
Description = Annotated[str, Field(max_length=2000)]
Priority = Literal["low", "normal", "high"]
TaskStatus = Literal["pending", "completed"]
EventStatus = Literal["scheduled", "cancelled"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TaskCreate(StrictModel):
    title: Title
    description: Description = ""
    priority: Priority = "normal"
    due_at: AwareDatetime | None = None


class TaskUpdate(StrictModel):
    title: Title | None = None
    description: Description | None = None
    priority: Priority | None = None
    status: TaskStatus | None = None
    due_at: AwareDatetime | None = None


class TaskId(StrictModel):
    task_id: int = Field(gt=0)


class TaskList(StrictModel):
    status: TaskStatus | None = None


class EventCreate(StrictModel):
    title: Title
    description: Description = ""
    start_at: AwareDatetime
    end_at: AwareDatetime
    timezone: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def valid_schedule(self):
        if self.end_at <= self.start_at:
            raise ValueError("Event end must be after start")
        try:
            zone = ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Unknown IANA timezone") from exc
        for value in (self.start_at, self.end_at):
            if value.utcoffset() != value.astimezone(zone).utcoffset():
                raise ValueError("Datetime offset does not match named timezone")
        return self


class EventUpdate(StrictModel):
    title: Title | None = None
    description: Description | None = None
    start_at: AwareDatetime | None = None
    end_at: AwareDatetime | None = None
    timezone: str | None = None
    location: str | None = Field(default=None, max_length=200)
    status: EventStatus | None = None


class EventId(StrictModel):
    event_id: int = Field(gt=0)


class DaySummary(StrictModel):
    day: date
    timezone: str = Field(default="UTC", min_length=1, max_length=100)


class ReminderCreate(StrictModel):
    message: Annotated[str, Field(min_length=1, max_length=500)]
    scheduled_at: AwareDatetime
    task_id: int | None = Field(default=None, gt=0)
    event_id: int | None = Field(default=None, gt=0)


class ReminderId(StrictModel):
    reminder_id: int = Field(gt=0)


class ChatInput(StrictModel):
    message: str = Field(min_length=1, max_length=2000)


class ApprovalDecision(StrictModel):
    confirmation_token: str = Field(min_length=20, max_length=150)


class ToolCall(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    arguments: dict = Field(default_factory=dict)
