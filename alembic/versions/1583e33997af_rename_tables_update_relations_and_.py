"""update tables, fields, and relations

Revision ID: 1583e33997af
Revises: 7e25ccd95566
Create Date: 2026-04-08 20:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1583e33997af'
down_revision = '7e25ccd95566'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    # Drop old tables (if exist)
    op.drop_table('refresh_tokens')
    op.drop_table('reports')
    op.drop_table('ai_bots')
    op.drop_table('job_applicants')
    op.drop_table('jobs')
    op.drop_table('users')
    op.drop_table('companies')

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('company_id', sa.Integer(), primary_key=True),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password', sa.String(255), nullable=True),
        sa.Column('profile_picture', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('role', sa.String(), server_default="'user'"),
        sa.Column('google_id', sa.String(), unique=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.company_id'), nullable=True)
    )

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('job_id', sa.Integer(), primary_key=True),
        sa.Column('job_title', sa.String(255), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('salary_range', sa.String(255), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.company_id'), nullable=False)
    )

    # Create job_applications junction table
    op.create_table(
        'job_applications',
        sa.Column('job_application_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.job_id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create ai_bots table
    op.create_table(
        'ai_bots',
        sa.Column('bot_id', sa.Integer(), primary_key=True),
        sa.Column('bot_name', sa.String(255), nullable=False),
        sa.Column('bot_type', sa.String(50), nullable=True),
        sa.Column('bot_description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'))
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('report_id', sa.Integer(), primary_key=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('result', sa.String(50), nullable=False),
        sa.Column('remarks', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('bot_id', sa.Integer(), sa.ForeignKey('ai_bots.bot_id'), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.company_id'), nullable=False)
    )

    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('interview_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), server_default="'pending'"),
        sa.Column('job_application_id', sa.Integer(), sa.ForeignKey('job_applications.job_application_id'), nullable=False),
        sa.Column('ai_bot_id', sa.Integer(), sa.ForeignKey('ai_bots.bot_id'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('interviews')
    op.drop_table('reports')
    op.drop_table('ai_bots')
    op.drop_table('job_applications')
    op.drop_table('jobs')
    op.drop_table('users')
    op.drop_table('companies')