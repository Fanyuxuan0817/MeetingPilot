from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Topic(BaseModel):
    title: str
    content: str
    source_chunk_ids: list[str]


class DecisionShort(BaseModel):
    topic: str
    decision: str
    source_chunk_ids: list[str]


class Risk(BaseModel):
    title: str
    level: RiskLevel
    description: str


class SummaryDetail(BaseModel):
    overview: str
    topics: list[Topic]
    decisions: list[DecisionShort]
    risks: list[Risk]
    open_questions: list[str]


class SummaryRead(BaseModel):
    meeting_id: str
    summary: SummaryDetail
    generated_at: datetime

