"""Модель записи о статусе задачи (история изменений)."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.item import Item


class Status(Base):
    """Запись в истории статусов задачи."""

    __tablename__ = "statuses"

    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связь с задачей
    item: Mapped["Item"] = relationship("Item", back_populates="statuses")

    def __repr__(self) -> str:
        return f"<Status id={self.id} item_id={self.item_id} date={self.status_date}>"
