from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


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


def _empty_str_to_none(v: str | None) -> str | None:
    if v == "":
        return None
    return v


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: Annotated[str | None, BeforeValidator(_empty_str_to_none)] = None
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

