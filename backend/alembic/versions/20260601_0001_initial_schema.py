"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-06-01 00:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Создание схемы v2.0 с нормализованной структурой.

    Идемпотентно: создаёт только отсутствующие таблицы. Это позволяет применять
    миграцию как на чистой БД (создаются все таблицы), так и на существующей
    базе v1 (создаётся только новая таблица item_executors — см. MIGRATION_GUIDE).
    """

    # Включаем WAL-режим и внешние ключи для SQLite
    op.execute("PRAGMA journal_mode=WAL")
    op.execute("PRAGMA foreign_keys=ON")

    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    # ── Таблица отделов ────────────────────────────────────────────────────────
    if "departments" not in existing:
        op.create_table(
            "departments",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(255), nullable=False, unique=True),
            sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_departments_id", "departments", ["id"])
        op.create_index("ix_departments_name", "departments", ["name"])

    # ── Таблица исполнителей ───────────────────────────────────────────────────
    if "executors" not in existing:
        op.create_table(
            "executors",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(255), nullable=False, unique=True),
            sa.Column(
                "department_id",
                sa.Integer,
                sa.ForeignKey("departments.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_executors_id", "executors", ["id"])
        op.create_index("ix_executors_name", "executors", ["name"])
        op.create_index("ix_executors_department_id", "executors", ["department_id"])

    # ── Таблица задач ──────────────────────────────────────────────────────────
    if "items" not in existing:
        op.create_table(
            "items",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("topic", sa.Text, nullable=False),
            sa.Column("ticket", sa.String(100), nullable=True),
            sa.Column("priority", sa.String(20), nullable=True),
            sa.Column("state", sa.String(20), nullable=False, server_default="in_progress"),
            sa.Column("due_date", sa.Date, nullable=True),
            # Сохраняем для совместимости при миграции данных из v1
            sa.Column("executors_json", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_items_id", "items", ["id"])
        op.create_index("ix_items_state", "items", ["state"])

    # ── Таблица статусов задач ─────────────────────────────────────────────────
    if "statuses" not in existing:
        op.create_table(
            "statuses",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column(
                "item_id",
                sa.Integer,
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("status_date", sa.Date, nullable=True),
            sa.Column("status_note", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_statuses_id", "statuses", ["id"])
        op.create_index("ix_statuses_item_id", "statuses", ["item_id"])

    # ── Таблица связи задача ↔ исполнитель (M2M) ───────────────────────────────
    if "item_executors" not in existing:
        op.create_table(
            "item_executors",
            sa.Column(
                "item_id",
                sa.Integer,
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column(
                "executor_id",
                sa.Integer,
                sa.ForeignKey("executors.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )

    # ── Приведение существующих таблиц v1 к схеме v2 ────────────────────────────
    # В v1 у departments/executors не было created_at, у items мог отсутствовать
    # executors_json. Добавляем недостающие столбцы (nullable — SQLite не допускает
    # ADD COLUMN с непостоянным default вроде CURRENT_TIMESTAMP для существующих строк).
    inspector = sa.inspect(bind)

    def add_missing(table: str, column: sa.Column) -> None:
        if table in existing:
            cols = {c["name"] for c in inspector.get_columns(table)}
            if column.name not in cols:
                op.add_column(table, column)

    add_missing("departments", sa.Column("created_at", sa.DateTime, nullable=True))
    add_missing("executors", sa.Column("created_at", sa.DateTime, nullable=True))
    add_missing("items", sa.Column("created_at", sa.DateTime, nullable=True))
    add_missing("items", sa.Column("executors_json", sa.Text, nullable=True))
    add_missing("statuses", sa.Column("created_at", sa.DateTime, nullable=True))


def downgrade() -> None:
    """Удаление всех таблиц."""
    op.drop_table("item_executors")
    op.drop_table("statuses")
    op.drop_table("items")
    op.drop_table("executors")
    op.drop_table("departments")
