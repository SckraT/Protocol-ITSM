"""add_meetings

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-03 00:00:00.000000

Добавляет сущность Meeting (совещание):
- таблица meetings
- M2M meeting_participants (совещание ↔ исполнитель)
- колонка items.meeting_id (FK → meetings, SET NULL)
Идемпотентна: проверяет наличие таблиц/колонок перед созданием.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать таблицы meetings, meeting_participants и колонку items.meeting_id."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    # 1. Таблица совещаний
    if "meetings" not in existing:
        op.create_table(
            "meetings",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("title", sa.Text, nullable=False),
            sa.Column("meeting_date", sa.Date, nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_meetings_id", "meetings", ["id"])

    # 2. M2M таблица участников
    if "meeting_participants" not in existing:
        op.create_table(
            "meeting_participants",
            sa.Column(
                "meeting_id",
                sa.Integer,
                sa.ForeignKey("meetings.id", ondelete="CASCADE"),
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

    # 3. Колонка items.meeting_id (если таблица items уже есть и колонки нет)
    if "items" in existing:
        cols = {c["name"] for c in inspector.get_columns("items")}
        if "meeting_id" not in cols:
            op.add_column("items", sa.Column(
                "meeting_id",
                sa.Integer,
                sa.ForeignKey("meetings.id", ondelete="SET NULL"),
                nullable=True,
            ))
            op.create_index("ix_items_meeting_id", "items", ["meeting_id"])


def downgrade() -> None:
    """Откат: удалить колонку и таблицы."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "items" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("items")}
        if "meeting_id" in cols:
            op.drop_index("ix_items_meeting_id", table_name="items")
            op.drop_column("items", "meeting_id")
    op.drop_table("meeting_participants")
    op.drop_table("meetings")
