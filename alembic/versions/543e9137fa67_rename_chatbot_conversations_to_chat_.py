"""rename chatbot_message to chat_messages

Revision ID: 543e9137fa67
Revises: 1eba0960e2c4
Create Date: 2026-04-28 12:23:38.296352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '543e9137fa67'
down_revision: Union[str, Sequence[str], None] = '1eba0960e2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table(
        "chatbot_message",
        "chat_messages"
    )

def downgrade():
    op.rename_table(
        "chat_messages",
        "chatbot_message"
    )
