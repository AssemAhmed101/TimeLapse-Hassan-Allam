"""initial database

Revision ID: 0001
Revises:
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=120), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cameras_id"), "cameras", ["id"], unique=False)

    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_system_settings_key"), "system_settings", ["key"], unique=True)

    op.create_table(
        "snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_snapshots_camera_id"), "snapshots", ["camera_id"], unique=False)
    op.create_index(op.f("ix_snapshots_captured_at"), "snapshots", ["captured_at"], unique=False)
    op.create_index(op.f("ix_snapshots_id"), "snapshots", ["id"], unique=False)

    op.create_table(
        "timelapses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timelapses_camera_id"), "timelapses", ["camera_id"], unique=False)
    op.create_index(op.f("ix_timelapses_id"), "timelapses", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_timelapses_id"), table_name="timelapses")
    op.drop_index(op.f("ix_timelapses_camera_id"), table_name="timelapses")
    op.drop_table("timelapses")

    op.drop_index(op.f("ix_snapshots_id"), table_name="snapshots")
    op.drop_index(op.f("ix_snapshots_captured_at"), table_name="snapshots")
    op.drop_index(op.f("ix_snapshots_camera_id"), table_name="snapshots")
    op.drop_table("snapshots")

    op.drop_index(op.f("ix_system_settings_key"), table_name="system_settings")
    op.drop_table("system_settings")

    op.drop_index(op.f("ix_cameras_id"), table_name="cameras")
    op.drop_table("cameras")
