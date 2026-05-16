from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class JobResponse(BaseModel):
    meeting_id: str
    job_id: str
    status: JobStatus
