"""Модель задачи протокола совещания."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.executor import Executor
    from app.models.status import Status


class Item(Base):
    """Задача из протокола совещания."""

    __tablename__ = "items"

    # Основные поля
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    ticket: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress", index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Сохраняем старое поле для совместимости при миграции данных из v1
    # ORM не использует это поле — только скрипт migrate_data.py
    executors_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связи
    executors: Mapped[list["Executor"]] = relationship(
        "Executor",
        secondary="item_executors",
        back_populates="items",
        lazy="selectin",
    )
    statuses: Mapped[list["Status"]] = relationship(
        "Status",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="Status.id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Item id={self.id} state={self.state!r} topic={self.topic[:30]!r}>"
