"""audit_log

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-05 01:00:00.000000

Создаёт таблицу audit_log для фиксации событий безопасности и действий с данными.
Идемпотентна: проверяет наличие таблицы перед созданием.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать таблицу audit_log (идемпотентно)."""
    bind = op.get_bind()
    if "audit_log" not in sa.inspect(bind).get_table_names():
        op.create_table(
            "audit_log",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("event_type", sa.String(50), nullable=False),
            sa.Column("username", sa.String(255), nullable=True),
            sa.Column("ip", sa.String(64), nullable=True),
            sa.Column("user_agent", sa.String(512), nullable=True),
            sa.Column("payload", sa.JSON, nullable=True),
        )
        op.create_index("ix_audit_log_id", "audit_log", ["id"])
        op.create_index("ix_audit_log_event_type", "audit_log", ["event_type"])


def downgrade() -> None:
    """Удалить таблицу audit_log."""
    op.drop_table("audit_log")
