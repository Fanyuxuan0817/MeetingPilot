from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    CANCELED = "canceled"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActionItemBase(BaseModel):
    task: str = Field(min_length=1)
    owner: str = Field(min_length=1, max_length=100)
    deadline: date | None = None
    priority: Priority = Priority.MEDIUM
    source_chunk_id: str | None = None


class ActionItemCreate(ActionItemBase):
    pass


class ActionItemUpdate(BaseModel):
    task: str | None = Field(default=None, min_length=1)
    owner: str | None = Field(default=None, min_length=1, max_length=100)
    deadline: date | None = None
    priority: Priority | None = None
    status: ActionStatus | None = None


class ActionItemRead(ActionItemBase):
    id: str
    meeting_id: str
    status: ActionStatus
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

