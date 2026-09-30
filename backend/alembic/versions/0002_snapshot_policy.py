"""snapshot policy

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "snapshot_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("retry_delay_seconds", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["camera_id"],
            ["cameras.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("camera_id"),
    )
    op.create_index(
        op.f("ix_snapshot_policies_camera_id"),
        "snapshot_policies",
        ["camera_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_snapshot_policies_id"),
        "snapshot_policies",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_snapshot_policies_id"),
        table_name="snapshot_policies",
    )
    op.drop_index(
        op.f("ix_snapshot_policies_camera_id"),
        table_name="snapshot_policies",
    )
    op.drop_table("snapshot_policies")
