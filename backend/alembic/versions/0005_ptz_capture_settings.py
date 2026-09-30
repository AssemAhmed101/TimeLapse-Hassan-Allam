"""PTZ capture settings

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.add_column(sa.Column("ptz_preset_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "ptz_settle_seconds",
                sa.Integer(),
                nullable=False,
                server_default="15",
            )
        )
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.alter_column("ptz_settle_seconds", server_default=None)

    # This release intentionally converts all existing capture policies to the
    # approved marketing schedule: one frame every six hours, day and night.
    op.execute(
        "UPDATE snapshot_policies "
        "SET interval_seconds = 21600, start_time = '00:00:00', "
        "end_time = '23:59:59'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE snapshot_policies "
        "SET interval_seconds = 300, start_time = '07:00:00', "
        "end_time = '18:00:00'"
    )
    with op.batch_alter_table("cameras") as batch_op:
        batch_op.drop_column("ptz_settle_seconds")
        batch_op.drop_column("ptz_preset_id")
