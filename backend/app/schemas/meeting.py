from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MeetingStatus(str, Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class MeetingBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class MeetingCreate(MeetingBase):
    started_at: datetime


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    tags: list[str] | None = None


class MeetingRead(MeetingBase):
    id: str
    status: MeetingStatus
    duration: float | None = 0.0
    audio_url: str | None = None
    language: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

