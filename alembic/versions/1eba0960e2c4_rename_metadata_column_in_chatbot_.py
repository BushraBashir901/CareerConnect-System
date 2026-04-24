"""rename metadata column in chatbot conversations

Revision ID: 1eba0960e2c4
Revises: 7bd2d14259e7
Create Date: 2026-04-24 12:40:46.192078
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1eba0960e2c4"
down_revision: Union[str, Sequence[str], None] = "7bd2d14259e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "chatbot_conversations",
        "metadata",
        new_column_name="conservation_metadata"
    )


def downgrade() -> None:
    op.alter_column(
        "chatbot_conversations",
        "conservation_metadata",
        new_column_name="metadata"
    )