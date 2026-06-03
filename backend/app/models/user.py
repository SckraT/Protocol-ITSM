"""
Модель пользователя с ролями.
Роли: viewer (чтение), editor (полный CRUD), admin (CRUD + управление пользователями).
"""
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


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
