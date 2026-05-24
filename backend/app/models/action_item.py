import uuid
from datetime import date, datetime

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ActionStatus:
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    CANCELED = "canceled"


class Priority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


action_status_enum = Enum(
    ActionStatus.TODO,
    ActionStatus.DOING,
    ActionStatus.DONE,
    ActionStatus.CANCELED,
    name="action_status",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)

priority_level_enum = Enum(
    Priority.LOW,
    Priority.MEDIUM,
    Priority.HIGH,
    Priority.URGENT,
    name="priority_level",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class ActionItem(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "action_item"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meeting.id", ondelete="CASCADE"),
        nullable=False,
    )
    task: Mapped[str] = mapped_column(nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(
        priority_level_enum,
        nullable=False,
        server_default=Priority.MEDIUM,
    )
    status: Mapped[str] = mapped_column(
        action_status_enum,
        nullable=False,
        server_default=ActionStatus.TODO,
    )
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transcript_chunk.id", ondelete="SET NULL"),
        nullable=True,
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")
    source_chunk: Mapped["TranscriptChunk | None"] = relationship(lazy="selectin")


from app.models.meeting import Meeting
from app.models.transcript import TranscriptChunk
