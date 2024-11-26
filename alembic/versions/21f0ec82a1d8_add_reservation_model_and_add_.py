"""Add reservation model and add relationship user and reservations

Revision ID: 21f0ec82a1d8
Revises: 430c565e86cc
Create Date: 2024-11-26 12:17:05.753355

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "21f0ec82a1d8"
down_revision: Union[str, None] = "430c565e86cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("exam_start_date", sa.DateTime(), nullable=False),
        sa.Column("exam_end_date", sa.DateTime(), nullable=False),
        sa.Column("applicants", sa.Integer(), nullable=False),
        sa.Column("status", postgresql.ENUM("PENDING", "CONFIRMED", name="reservation_status"), nullable=True),
        sa.Column("time_range", postgresql.TSTZRANGE(), nullable=False),
        sa.CheckConstraint("exam_end_date > exam_start_date", name="check_exam_time_valid"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reservations_exam_date", "reservations", ["exam_date"], unique=False)
    op.create_index(
        "idx_reservations_time_range", "reservations", ["time_range"], unique=False, postgresql_using="gist"
    )
    op.create_index(op.f("ix_reservations_id"), "reservations", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_reservations_id"), table_name="reservations")
    op.drop_index("idx_reservations_time_range", table_name="reservations", postgresql_using="gist")
    op.drop_index("idx_reservations_exam_date", table_name="reservations")
    op.drop_table("reservations")
    # ### end Alembic commands ###
