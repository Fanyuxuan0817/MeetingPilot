from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    meeting_id: str
    chunk_id: str
    speaker: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    text: str


class QARequest(BaseModel):
    meeting_id: str | None = None
    question: str = Field(min_length=1)
    scope: Literal["current_meeting", "all_meetings"] = "current_meeting"


class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]


class WSMessage(BaseModel):
    type: Literal["start", "chunk", "end", "error", "job_progress"]
    message: str | None = ""
    job_id: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    citations: list[Citation] | None = None
