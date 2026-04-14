"""create refresh_tokens table

Revision ID: b06caab547d8
Revises: caef8e9084d0
Create Date: 2026-04-09

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'b06caab547d8'
down_revision: Union[str, Sequence[str], None] = 'caef8e9084d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('refresh_tokens')