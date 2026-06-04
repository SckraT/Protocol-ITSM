"""
Модель пользователя с ролями.
Роли: viewer (чтение), editor (полный CRUD), admin (CRUD + управление пользователями).
"""
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.executor import Executor


class RoleEnum(str, Enum):
    """Роли пользователей."""

    viewer = "viewer"   # только чтение
    editor = "editor"   # CRUD задач и справочников
    admin = "admin"     # editor + управление пользователями


class User(Base):
    """Модель пользователя системы."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default=RoleEnum.viewer, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # ФИО (Фамилия/Имя/Отчество). Обязательность — на уровне схем, в БД nullable.
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Контакты (опциональны, используются как альтернативные идентификаторы входа)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)

    # Обратная связь 1:1 с исполнителем (Executor.user_id)
    executor: Mapped["Executor | None"] = relationship(
        "Executor",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )

    @property
    def executor_id(self) -> int | None:
        """ID привязанного исполнителя (для сериализации)."""
        return self.executor.id if self.executor else None

    @property
    def display_name(self) -> str:
        """«Фамилия И.О.» из ФИО; если фамилия пуста → username (legacy/seed)."""
        if not self.last_name:
            return self.username
        initials = ""
        if self.first_name:
            initials += f" {self.first_name[0].upper()}."
        if self.middle_name:
            initials += f"{self.middle_name[0].upper()}."
        return f"{self.last_name}{initials}"
