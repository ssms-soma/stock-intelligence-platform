"""Create saved research table.

Revision ID: a73e92c4d601
Revises: 908bb8f1f14b
"""
from alembic import op
import sqlalchemy as sa

revision = "a73e92c4d601"
down_revision = "908bb8f1f14b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_research",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(32), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_research_user_id_created_at_id", "saved_research",
                    ["user_id", "created_at", "id"])


def downgrade() -> None:
    op.drop_index("ix_saved_research_user_id_created_at_id", table_name="saved_research")
    op.drop_table("saved_research")
