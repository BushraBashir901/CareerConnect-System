"""Add google_id, role to users and create refresh_tokens table

Revision ID: d649239bfa8c
Revises: 0d3a5061906a
Create Date: 2026-04-08 00:33:12.164910
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd649239bfa8c'
down_revision = '0d3a5061906a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema"""
    # Add google_id column to users
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    

    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema"""
    # Drop refresh_tokens table
    op.drop_table('refresh_tokens')
    
    # Drop role column
    op.drop_column('users', 'role')
    
    # Drop google_id column
    op.drop_column('users', 'google_id')