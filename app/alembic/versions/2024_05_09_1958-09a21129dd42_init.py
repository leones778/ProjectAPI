"""init

Revision ID: 09a21129dd42
Revises:
Create Date: 2024-05-09 19:58:17.276179

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "09a21129dd42"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consumable_categories",
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("middle_name", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.Date(), nullable=False),
        sa.Column(
            "role", postgresql.ENUM("ADMIN", "WORKER", name="role_enum"), nullable=False
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "user_sessions",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expiration_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_table(
        "consumables",
        sa.Column("consumable_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["consumable_categories.category_id"],
        ),
        sa.PrimaryKeyConstraint("consumable_id"),
    )
    op.create_table(
        "consumable_history",
        sa.Column("history_id", sa.Integer(), nullable=False),
        sa.Column("modified_count", sa.Integer(), nullable=False),
        sa.Column("modified_time", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("consumable_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["consumable_id"],
            ["consumables.consumable_id"],
        ),
        sa.PrimaryKeyConstraint("history_id"),
    )


def downgrade() -> None:
    op.drop_table("consumable_history")
    op.drop_table("consumables")
    op.drop_table("user_sessions")
    op.drop_table("consumable_categories")
    op.drop_table("users")
    op.execute("DROP TYPE role_enum;")
