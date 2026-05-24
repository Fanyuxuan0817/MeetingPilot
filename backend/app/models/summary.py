import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


risk_level_enum = Enum(
    RiskLevel.LOW,
    RiskLevel.MEDIUM,
    RiskLevel.HIGH,
    name="risk_level",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class Summary(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "summary"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    overview: Mapped[str] = mapped_column(nullable=False)
    embedding = mapped_column(Vector(1536), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="summary")
    topics: Mapped[list["SummaryTopic"]] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SummaryTopic.sort_order",
    )
    decisions: Mapped[list["SummaryDecision"]] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SummaryDecision.sort_order",
    )
    risks: Mapped[list["SummaryRisk"]] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SummaryRisk.sort_order",
    )
    open_questions: Mapped[list["SummaryOpenQuestion"]] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SummaryOpenQuestion.sort_order",
    )


class SummaryTopic(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "summary_topic"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    summary: Mapped["Summary"] = relationship(back_populates="topics")
    sources: Mapped[list["SummaryTopicSource"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SummaryTopicSource(Base):
    __tablename__ = "summary_topic_source"

    summary_topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary_topic.id", ondelete="CASCADE"),
        primary_key=True,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="CASCADE"),
        primary_key=True,
    )

    topic: Mapped["SummaryTopic"] = relationship(back_populates="sources")
    chunk: Mapped["TranscriptChunk"] = relationship(lazy="noload")


class SummaryDecision(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "summary_decision"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    decision: Mapped[str] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    summary: Mapped["Summary"] = relationship(back_populates="decisions")
    sources: Mapped[list["SummaryDecisionSource"]] = relationship(
        back_populates="decision",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SummaryDecisionSource(Base):
    __tablename__ = "summary_decision_source"

    summary_decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary_decision.id", ondelete="CASCADE"),
        primary_key=True,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="CASCADE"),
        primary_key=True,
    )

    decision: Mapped["SummaryDecision"] = relationship(back_populates="sources")
    chunk: Mapped["TranscriptChunk"] = relationship(lazy="noload")


class SummaryRisk(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "summary_risk"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(risk_level_enum, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    summary: Mapped["Summary"] = relationship(back_populates="risks")


class SummaryOpenQuestion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "summary_open_question"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("summary.id", ondelete="CASCADE"),
        nullable=False,
    )
    question: Mapped[str] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    summary: Mapped["Summary"] = relationship(back_populates="open_questions")


from app.models.transcript import TranscriptChunk
