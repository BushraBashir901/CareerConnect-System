from alembic import op
import sqlalchemy as sa


revision = '2ab26136801b'
down_revision = '93da3cd728a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'user_resume',
        sa.Column('file_path', sa.String(), nullable=True)
    )

    op.add_column(
        'user_resume',
        sa.Column('filename', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('user_resume', 'file_path')
    op.drop_column('user_resume', 'filename')