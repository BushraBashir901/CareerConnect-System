"""Add user_resume table

Revision ID: b2f8db845aa2
Revises: add_team_invitations_table
Create Date: 2026-04-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2f8db845aa2'
down_revision: Union[str, Sequence[str], None] = 'add_team_invitations_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table(
        'user_resume',
        sa.Column('user_resume_id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.String(), nullable=False),
        sa.Column('clear_text', postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_table('user_resume')