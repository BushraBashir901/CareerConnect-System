"""rename conservation_metadata to conversation_metadata

Revision ID: 591f61c5ee52
Revises: 543e9137fa67
Create Date: 2026-04-28 13:02:37.389377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '591f61c5ee52'
down_revision: Union[str, Sequence[str], None] = '543e9137fa67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "chat_messages",
        "conservation_metadata",
        new_column_name="conversation_metadata"
    )


def downgrade() -> None:
    op.alter_column(
        "chat_messages",
        "conversation_metadata",
        new_column_name="conservation_metadata"
    )
