"""Модель исполнителя (справочник)."""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.item import Item


class Executor(Base):
    """Исполнитель — справочник для назначения на задачи."""

    __tablename__ = "executors"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # FK на отдел, NULL при удалении отдела (SET NULL)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Связи
    department: Mapped["Department | None"] = relationship(
        "Department",
        back_populates="executors",
        lazy="selectin",
    )
    items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary="item_executors",
        back_populates="executors",
    )

    def __repr__(self) -> str:
        return f"<Executor id={self.id} name={self.name!r}>"
