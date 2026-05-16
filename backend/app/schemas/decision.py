from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ConflictLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionRead(BaseModel):
    id: str
    topic: str
    decision: str
    version: int
    source_chunk_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionConflictRead(BaseModel):
    id: str
    topic: str
    current_decision: str
    previous_decision: str
    level: ConflictLevel
    description: str
    current_source_chunk_id: str
    previous_meeting_id: str

    model_config = {"from_attributes": True}

