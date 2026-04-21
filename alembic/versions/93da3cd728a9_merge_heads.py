"""merge heads

Revision ID: 93da3cd728a9
Revises: b2f8db845aa2, f65a69d701de
Create Date: 2026-04-20 16:26:37.308426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93da3cd728a9'
down_revision: Union[str, Sequence[str], None] = ('b2f8db845aa2', 'f65a69d701de')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
