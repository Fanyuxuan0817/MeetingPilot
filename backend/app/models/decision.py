import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ConflictLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


conflict_level_enum = Enum(
    ConflictLevel.LOW,
    ConflictLevel.MEDIUM,
    ConflictLevel.HIGH,
    name="conflict_level",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class DecisionRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "decision_record"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(nullable=False)
    decision: Mapped[str] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, server_default="1")
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="RESTRICT"),
        nullable=False,
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="decision_records")
    source_chunk: Mapped["TranscriptChunk"] = relationship(lazy="selectin")


class DecisionConflict(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "decision_conflict"

    topic: Mapped[str] = mapped_column(nullable=False)
    current_decision: Mapped[str] = mapped_column(nullable=False)
    previous_decision: Mapped[str] = mapped_column(nullable=False)
    level: Mapped[str] = mapped_column(conflict_level_enum, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    current_source_chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="RESTRICT"),
        nullable=False,
    )
    previous_meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )

    current_source_chunk: Mapped["TranscriptChunk"] = relationship(lazy="selectin")
    previous_meeting: Mapped["Meeting"] = relationship(lazy="selectin")


from app.models.meeting import Meeting
from app.models.transcript import TranscriptChunk
