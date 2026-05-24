import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class MeetingStatus:
    CREATED = "created"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


meeting_status_enum = Enum(
    MeetingStatus.CREATED,
    MeetingStatus.UPLOADING,
    MeetingStatus.TRANSCRIBING,
    MeetingStatus.ANALYZING,
    MeetingStatus.COMPLETED,
    MeetingStatus.FAILED,
    name="meeting_status",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class Meeting(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "meeting"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        meeting_status_enum,
        nullable=False,
        server_default=MeetingStatus.CREATED,
    )
    duration: Mapped[float] = mapped_column(nullable=False, server_default="0.0")
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    tags: Mapped[list["MeetingTag"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    transcript_chunks: Mapped[list["TranscriptChunk"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    decision_records: Mapped[list["DecisionRecord"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    summary: Mapped["Summary | None"] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
        lazy="noload",
    )


class MeetingTag(Base):
    __tablename__ = "meeting_tag"
    __table_args__ = (
        UniqueConstraint("meeting_id", "tag", name="uq_meeting_tag"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False)

    meeting: Mapped["Meeting"] = relationship(back_populates="tags")


from app.models.action_item import ActionItem
from app.models.decision import DecisionRecord
from app.models.job import Job
from app.models.summary import Summary
from app.models.transcript import TranscriptChunk
