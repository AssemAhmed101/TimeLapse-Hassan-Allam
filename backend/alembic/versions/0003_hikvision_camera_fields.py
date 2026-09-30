"""hikvision camera fields

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.add_column(
            sa.Column("password", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("scheme", sa.String(length=10), nullable=False, server_default="http")
        )
        batch_op.add_column(
            sa.Column("port", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("channel", sa.Integer(), nullable=False, server_default="1")
        )

    with op.batch_alter_table("cameras") as batch_op:
        batch_op.alter_column("scheme", server_default=None)
        batch_op.alter_column("channel", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.drop_column("channel")
        batch_op.drop_column("port")
        batch_op.drop_column("scheme")
        batch_op.drop_column("password")
