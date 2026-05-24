"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-05-21 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    meeting_status = postgresql.ENUM(
        'created', 'uploading', 'transcribing', 'analyzing', 'completed', 'failed',
        name='meeting_status', create_type=False
    )
    action_status = postgresql.ENUM(
        'todo', 'doing', 'done', 'canceled',
        name='action_status', create_type=False
    )
    priority_level = postgresql.ENUM(
        'low', 'medium', 'high', 'urgent',
        name='priority_level', create_type=False
    )
    conflict_level = postgresql.ENUM(
        'low', 'medium', 'high',
        name='conflict_level', create_type=False
    )
    risk_level = postgresql.ENUM(
        'low', 'medium', 'high',
        name='risk_level', create_type=False
    )
    job_status = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed',
        name='job_status', create_type=False
    )
    qa_scope = postgresql.ENUM(
        'current_meeting', 'all_meetings',
        name='qa_scope', create_type=False
    )

    op.execute("CREATE TYPE meeting_status AS ENUM ('created', 'uploading', 'transcribing', 'analyzing', 'completed', 'failed')")
    op.execute("CREATE TYPE action_status AS ENUM ('todo', 'doing', 'done', 'canceled')")
    op.execute("CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent')")
    op.execute("CREATE TYPE conflict_level AS ENUM ('low', 'medium', 'high')")
    op.execute("CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high')")
    op.execute("CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed')")
    op.execute("CREATE TYPE qa_scope AS ENUM ('current_meeting', 'all_meetings')")

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create tables
    op.create_table(
        'meeting',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', meeting_status, nullable=False, server_default='created'),
        sa.Column('duration', sa.Double(), nullable=False, server_default='0.0'),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'meeting_tag',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag', sa.String(50), nullable=False),
        sa.UniqueConstraint('meeting_id', 'tag', name='uq_meeting_tag'),
    )

    op.create_table(
        'transcript_chunk',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker', sa.String(100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('start', sa.Double(), nullable=False),
        sa.Column('end', sa.Double(), nullable=False),
        sa.Column('confidence', sa.Double(), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('"start" >= 0', name='ck_chunk_start_nonneg'),
        sa.CheckConstraint('"end" >= 0', name='ck_chunk_end_nonneg'),
        sa.CheckConstraint('confidence >= 0 AND confidence <= 1', name='ck_chunk_confidence_range'),
    )
    op.execute("ALTER TABLE transcript_chunk ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)")

    op.create_table(
        'action_item',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task', sa.Text(), nullable=False),
        sa.Column('owner', sa.String(100), nullable=False),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('priority', priority_level, nullable=False, server_default='medium'),
        sa.Column('status', action_status, nullable=False, server_default='todo'),
        sa.Column('source_chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'decision_record',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('decision', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source_chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'decision_conflict',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('current_decision', sa.Text(), nullable=False),
        sa.Column('previous_decision', sa.Text(), nullable=False),
        sa.Column('level', conflict_level, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('current_source_chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('previous_meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'summary',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('overview', sa.Text(), nullable=False),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("ALTER TABLE summary ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)")

    op.create_table(
        'summary_topic',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'summary_topic_source',
        sa.Column('summary_topic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary_topic.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'summary_decision',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('decision', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'summary_decision_source',
        sa.Column('summary_decision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary_decision.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'summary_risk',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('level', risk_level, nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'summary_open_question',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summary.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'job',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', job_status, nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'qa_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='SET NULL'), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('scope', qa_scope, nullable=False, server_default='current_meeting'),
        sa.Column('question_embedding', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("ALTER TABLE qa_history ALTER COLUMN question_embedding TYPE vector(1536) USING question_embedding::vector(1536)")

    op.create_table(
        'qa_citation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('qa_history_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('qa_history.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcript_chunk.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker', sa.String(100), nullable=False),
        sa.Column('start', sa.Double(), nullable=False),
        sa.Column('end', sa.Double(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.CheckConstraint('"start" >= 0', name='ck_citation_start_nonneg'),
        sa.CheckConstraint('"end" >= 0', name='ck_citation_end_nonneg'),
    )

    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index('idx_meeting_status', 'meeting', ['status'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_meeting_started_at', 'meeting', ['started_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_meeting_created_at', 'meeting', ['created_at'], postgresql_where=sa.text('deleted_at IS NULL'))

    op.create_index('idx_meeting_tag_meeting_id', 'meeting_tag', ['meeting_id'])
    op.create_index('idx_meeting_tag_tag', 'meeting_tag', ['tag'])

    op.create_index('idx_chunk_meeting_id', 'transcript_chunk', ['meeting_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_chunk_speaker', 'transcript_chunk', ['speaker'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_chunk_start_time', 'transcript_chunk', ['meeting_id', 'start'], postgresql_where=sa.text('deleted_at IS NULL'))

    op.create_index('idx_action_meeting_id', 'action_item', ['meeting_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_action_owner', 'action_item', ['owner'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_action_status', 'action_item', ['status'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_action_deadline', 'action_item', ['deadline'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_action_source_chunk', 'action_item', ['source_chunk_id'], postgresql_where=sa.text('deleted_at IS NULL'))

    op.create_index('idx_decision_meeting_id', 'decision_record', ['meeting_id'])
    op.create_index('idx_decision_topic', 'decision_record', ['topic'])
    op.create_index('idx_decision_source', 'decision_record', ['source_chunk_id'])

    op.create_index('idx_conflict_previous_meeting', 'decision_conflict', ['previous_meeting_id'])
    op.create_index('idx_conflict_level', 'decision_conflict', ['level'])
    op.create_index('idx_conflict_current_chunk', 'decision_conflict', ['current_source_chunk_id'])

    op.create_index('idx_summary_meeting_id', 'summary', ['meeting_id'])

    op.create_index('idx_summary_topic_summary_id', 'summary_topic', ['summary_id'])
    op.create_index('idx_summary_decision_summary_id', 'summary_decision', ['summary_id'])
    op.create_index('idx_summary_risk_summary_id', 'summary_risk', ['summary_id'])
    op.create_index('idx_summary_question_summary_id', 'summary_open_question', ['summary_id'])

    op.create_index('idx_job_meeting_id', 'job', ['meeting_id'])
    op.create_index('idx_job_status', 'job', ['status'])

    op.create_index('idx_qa_meeting_id', 'qa_history', ['meeting_id'])
    op.create_index('idx_qa_created_at', 'qa_history', ['created_at'])

    op.create_index('idx_citation_qa_history_id', 'qa_citation', ['qa_history_id'])
    op.create_index('idx_citation_chunk_id', 'qa_citation', ['chunk_id'])

    # Create HNSW indexes for pgvector
    op.execute("CREATE INDEX idx_chunk_embedding ON transcript_chunk USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")
    op.execute("CREATE INDEX idx_summary_embedding ON summary USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")
    op.execute("CREATE INDEX idx_qa_question_embedding ON qa_history USING hnsw (question_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")


def downgrade() -> None:
    # Drop tables
    op.drop_table('qa_citation')
    op.drop_table('qa_history')
    op.drop_table('job')
    op.drop_table('summary_open_question')
    op.drop_table('summary_risk')
    op.drop_table('summary_decision_source')
    op.drop_table('summary_decision')
    op.drop_table('summary_topic_source')
    op.drop_table('summary_topic')
    op.drop_table('summary')
    op.drop_table('decision_conflict')
    op.drop_table('decision_record')
    op.drop_table('action_item')
    op.drop_table('transcript_chunk')
    op.drop_table('meeting_tag')
    op.drop_table('meeting')
    op.drop_table('user')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS qa_scope")
    op.execute("DROP TYPE IF EXISTS job_status")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS conflict_level")
    op.execute("DROP TYPE IF EXISTS priority_level")
    op.execute("DROP TYPE IF EXISTS action_status")
    op.execute("DROP TYPE IF EXISTS meeting_status")
