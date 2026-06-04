"""auth_contacts_executor_user

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-04 00:00:00.000000

Добавляет:
- users.email, users.phone (опциональные, уникальные — альтернативные идентификаторы входа)
- executors.user_id (FK → users, SET NULL, unique) — привязка Исполнителя к УЗ 1:1
Идемпотентна: проверяет наличие колонок перед добавлением.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавить контакты в users и привязку user_id в executors."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. users.email / users.phone
    if "users" in inspector.get_table_names():
        user_cols = {c["name"] for c in inspector.get_columns("users")}
        if "email" not in user_cols:
            op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
            op.create_index("ix_users_email", "users", ["email"], unique=True)
        if "phone" not in user_cols:
            op.add_column("users", sa.Column("phone", sa.String(32), nullable=True))
            op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # 2. executors.user_id
    if "executors" in inspector.get_table_names():
        exec_cols = {c["name"] for c in inspector.get_columns("executors")}
        if "user_id" not in exec_cols:
            op.add_column("executors", sa.Column(
                "user_id",
                sa.Integer,
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ))
            op.create_index("ix_executors_user_id", "executors", ["user_id"], unique=True)


def downgrade() -> None:
    """Откат: удалить добавленные колонки и индексы."""
    op.drop_index("ix_executors_user_id", table_name="executors")
    op.drop_column("executors", "user_id")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_column("users", "phone")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")
