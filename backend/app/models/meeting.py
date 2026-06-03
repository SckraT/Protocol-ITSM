"""Модель совещания: группирует задачи по проекту/встрече."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.executor import Executor
    from app.models.item import Item


class Meeting(Base):
    """Совещание — тема, дата, участники; к нему привязываются задачи."""

    __tablename__ = "meetings"

    # Основные поля
    title: Mapped[str] = mapped_column(Text, nullable=False)
    meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Участники — исполнители через M2M
    participants: Mapped[list["Executor"]] = relationship(
        "Executor",
        secondary="meeting_participants",
        lazy="selectin",
    )
    # Задачи совещания (для счётчика item_count)
    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="meeting",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Meeting id={self.id} title={self.title[:30]!r}>"
