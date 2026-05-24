import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Double, ForeignKey, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TranscriptChunk(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "transcript_chunk"
    __table_args__ = (
        CheckConstraint("start >= 0", name="ck_chunk_start_nonneg"),
        CheckConstraint("end >= 0", name="ck_chunk_end_nonneg"),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name="ck_chunk_confidence_range"
        ),
    )

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )
    speaker: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    start: Mapped[float] = mapped_column(Double, nullable=False)
    end: Mapped[float] = mapped_column(Double, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Double, nullable=True)
    embedding = mapped_column(Vector(1536), nullable=True)

    meeting: Mapped["Meeting"] = relationship(back_populates="transcript_chunks")


from app.models.meeting import Meeting
