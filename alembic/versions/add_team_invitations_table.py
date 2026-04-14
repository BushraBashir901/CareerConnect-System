"""Add team_invitations table

Revision ID: add_team_invitations_table
Revises: caef8e9084d0
Create Date: 2026-04-14 12:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_team_invitations_table'
down_revision = 'caef8e9084d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create team_invitations table
    op.create_table('team_invitations',
        sa.Column('invitation_id', sa.String(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('invited_email', sa.String(length=255), nullable=False),
        sa.Column('invited_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'EXPIRED', 'REVOKED', name='invitationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ),
        sa.ForeignKeyConstraint(['invited_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('invitation_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_team_invitations_invited_email'), 'team_invitations', ['invited_email'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_team_invitations_invited_email'), table_name='team_invitations')
    
    # Drop table
    op.drop_table('team_invitations')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS invitationstatus')
