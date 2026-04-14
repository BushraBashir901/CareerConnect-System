"""delete table ai_bot_applicants

Revision ID: 7e25ccd95566
Revises: d649239bfa8c
Create Date: 2026-04-08 16:39:22.755972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e25ccd95566'
down_revision: Union[str, Sequence[str], None] = 'd649239bfa8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.drop_table("ai_bot_applicants")


def downgrade():
    op.create_table(
        "ai_bot_applicants",
        sa.Column("bot_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),

        sa.ForeignKeyConstraint(["bot_id"], ["ai_bots.bot_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),

        sa.PrimaryKeyConstraint("bot_id", "user_id")
    )