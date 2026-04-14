"""Add job_application_id FK to reports safely

Revision ID: caef8e9084d0
Revises: 1583e33997af
Create Date: 2026-04-09 16:23:42.689270
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'caef8e9084d0'
down_revision = '1583e33997af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema by adding job_application_id to reports"""
    # Add column
    op.add_column('reports', sa.Column('job_application_id', sa.Integer(), nullable=False))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'reports_job_application_id_fkey',  # constraint name
        'reports',  # source table
        'job_applications',  # target table
        ['job_application_id'],  # source column
        ['job_application_id']  # target column
    )


def downgrade() -> None:
    """Downgrade schema by removing job_application_id from reports"""
    # Drop foreign key constraint
    op.drop_constraint('reports_job_application_id_fkey', 'reports', type_='foreignkey')
    
    # Drop column
    op.drop_column('reports', 'job_application_id')