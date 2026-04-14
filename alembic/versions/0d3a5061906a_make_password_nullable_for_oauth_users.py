from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0d3a5061906a'
down_revision = '81a5d6f06822'
branch_labels = None
depends_on = None


def upgrade():
    """Make password nullable for OAuth users"""
    op.alter_column('users', 'password',
               existing_type=sa.String(length=255),
               nullable=True)


def downgrade():
    """Revert password to not nullable"""
    op.alter_column('users', 'password',
               existing_type=sa.String(length=255),
               nullable=False)