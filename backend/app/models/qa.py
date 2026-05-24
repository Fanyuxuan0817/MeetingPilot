import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Double, Enum, ForeignKey, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class QAScope:
    CURRENT_MEETING = "current_meeting"
    ALL_MEETINGS = "all_meetings"


qa_scope_enum = Enum(
    QAScope.CURRENT_MEETING,
    QAScope.ALL_MEETINGS,
    name="qa_scope",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class QAHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "qa_history"

    meeting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="SET NULL"),
        nullable=True,
    )
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    scope: Mapped[str] = mapped_column(
        qa_scope_enum,
        nullable=False,
        server_default=QAScope.CURRENT_MEETING,
    )
    question_embedding = mapped_column(Vector(1536), nullable=True)

    meeting: Mapped["Meeting | None"] = relationship(lazy="selectin")
    citations: Mapped[list["QACitation"]] = relationship(
        back_populates="qa_history",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QACitation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "qa_citation"
    __table_args__ = (
        CheckConstraint("start >= 0", name="ck_citation_start_nonneg"),
        CheckConstraint("end >= 0", name="ck_citation_end_nonneg"),
    )

    qa_history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_history.id", ondelete="CASCADE"),
        nullable=False,
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="CASCADE"),
        nullable=False,
    )
    speaker: Mapped[str] = mapped_column(String(100), nullable=False)
    start: Mapped[float] = mapped_column(Double, nullable=False)
    end: Mapped[float] = mapped_column(Double, nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)

    qa_history: Mapped["QAHistory"] = relationship(back_populates="citations")
    meeting: Mapped["Meeting"] = relationship(lazy="noload")
    chunk: Mapped["TranscriptChunk"] = relationship(lazy="noload")


from app.models.meeting import Meeting
from app.models.transcript import TranscriptChunk
