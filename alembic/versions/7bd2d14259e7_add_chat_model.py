"""add-chat-model

Revision ID: 7bd2d14259e7
Revises: 55783cff139b
Create Date: 2026-04-23 19:46:24.792637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bd2d14259e7'
down_revision: Union[str, Sequence[str], None] = '55783cff139b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================
    # CHATBOT TABLE
    # =========================
    op.create_table(
        'chatbot_conversations',
        sa.Column('conversation_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
    )

    # =========================
    # SAFE INDEX CREATION
    # (prevents crash if already exists)
    # =========================
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT to_regclass('public.idx_job_embedding');
        """)
    ).scalar()

    if not result:
        op.create_index(
            'idx_job_embedding',
            'jobs',
            ['embedding'],
            unique=False,
            postgresql_using='ivfflat',
            postgresql_ops={'embedding': 'vector_cosine_ops'},
            postgresql_with={'lists': '100'}
        )


def downgrade() -> None:
    # Drop chatbot table
    op.drop_table('chatbot_conversations')

    # Drop index safely
    op.drop_index('idx_job_embedding', table_name='jobs')