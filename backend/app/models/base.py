"""
Базовый класс для всех моделей SQLAlchemy 2.0.
Использует DeclarativeBase с типизированными Mapped-полями.
"""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.utils.time import utcnow


class Base(DeclarativeBase):
    """Базовая модель с общими полями id и created_at."""

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
