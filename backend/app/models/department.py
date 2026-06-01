"""Модель отдела (справочник)."""
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.executor import Executor


class Department(Base):
    """Отдел — справочник для группировки исполнителей."""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Связь с исполнителями (при удалении отдела department_id у исполнителей → NULL)
    executors: Mapped[list["Executor"]] = relationship(
        "Executor",
        back_populates="department",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"
