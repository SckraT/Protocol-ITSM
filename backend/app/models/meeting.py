"""Модель совещания: группирует задачи по проекту/встрече."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Text
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

    # Участники — исполнители через M2M. lazy="selectin" нужен для записи коллекции
    # (update_participants) в async-контексте. На списке задач каскад подавляется
    # через noload(Meeting.participants) в ItemRepository.
    participants: Mapped[list["Executor"]] = relationship(
        "Executor",
        secondary="meeting_participants",
        lazy="selectin",
    )
    # Задачи совещания. Счётчик item_count считается отдельным COUNT-запросом,
    # коллекцию не предзагружаем (иначе грузили бы все строки задач). Запись идёт
    # со стороны Item.meeting_id, поэтому ленивая стратегия по умолчанию безопасна.
    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="meeting",
    )

    def __repr__(self) -> str:
        return f"<Meeting id={self.id} title={self.title[:30]!r}>"
