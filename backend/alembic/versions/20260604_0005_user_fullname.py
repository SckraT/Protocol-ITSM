"""user_fullname

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-04 01:00:00.000000

Добавляет ФИО пользователя: last_name, first_name, middle_name (String(100), nullable).
Идемпотентна: проверяет наличие колонок перед добавлением.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавить поля ФИО в users."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("users")}
        if "last_name" not in cols:
            op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
        if "first_name" not in cols:
            op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
        if "middle_name" not in cols:
            op.add_column("users", sa.Column("middle_name", sa.String(100), nullable=True))


def downgrade() -> None:
    """Откат: удалить поля ФИО."""
    op.drop_column("users", "middle_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "last_name")
