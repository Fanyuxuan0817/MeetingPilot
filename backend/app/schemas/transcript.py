import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TranscriptChunkBase(BaseModel):
    speaker: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class TranscriptChunkUpdate(BaseModel):
    speaker: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


class TranscriptChunkRead(TranscriptChunkBase):
    id: uuid.UUID
    meeting_id: uuid.UUID
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TranscriptListRead(BaseModel):
    meeting_id: uuid.UUID
    chunks: list[TranscriptChunkRead]

