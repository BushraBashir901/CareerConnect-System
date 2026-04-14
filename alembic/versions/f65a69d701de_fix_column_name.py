from alembic import op

# revision identifiers
revision = 'f65a69d701de'
down_revision = 'b06caab547d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # rename column (remove extra "s")
    op.alter_column(
        "reports",
        "job_applications_id",
        new_column_name="job_application_id"
    )


def downgrade() -> None:
    # revert change
    op.alter_column(
        "reports",
        "job_application_id",
        new_column_name="job_applications_id"
    )