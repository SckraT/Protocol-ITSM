"""add_users

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-02 00:00:00.000000

Добавляет таблицу users для многопользовательской авторизации (v2.1).
Идемпотентна: проверяет наличие таблицы перед созданием.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать таблицу users (идемпотентно)."""
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    if "users" not in existing:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("username", sa.String, nullable=False, unique=True),
            sa.Column("hashed_password", sa.String, nullable=False),
            sa.Column("role", sa.String, nullable=False, server_default="viewer"),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    """Удалить таблицу users."""
    op.drop_table("users")
