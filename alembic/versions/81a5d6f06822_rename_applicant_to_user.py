"""Rename Applicant to User and add role column

Revision ID: 81a5d6f06822
Revises: 2762c175a875
Create Date: 2026-04-07
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '81a5d6f06822'
down_revision = '2762c175a875'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename applicants table to users"""
    # Rename table
    op.rename_table('applicants', 'users')


def downgrade() -> None:
    """Revert users table back to applicants"""

    # Rename table back
    op.rename_table('users', 'applicants')