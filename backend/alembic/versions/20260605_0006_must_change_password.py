"""must_change_password

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-05 00:00:00.000000

Добавляет users.must_change_password (Boolean, default false).
Идемпотентна: проверяет наличие колонки перед добавлением.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавить флаг must_change_password в users."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("users")}
        if "must_change_password" not in cols:
            op.add_column(
                "users",
                sa.Column("must_change_password", sa.Boolean, nullable=False, server_default=sa.false()),
            )


def downgrade() -> None:
    """Откат: удалить флаг."""
    op.drop_column("users", "must_change_password")
