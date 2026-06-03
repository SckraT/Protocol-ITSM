"""
Pydantic-схемы для управления пользователями (Admin-панель).
"""
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.user import RoleEnum


class UserCreate(BaseModel):
    """Создание нового пользователя."""

    username: str
    password: str
    role: RoleEnum = RoleEnum.viewer

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Имя пользователя не может быть пустым")
        if len(v) < 3:
            raise ValueError("Имя пользователя должно содержать минимум 3 символа")
        return v

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")
        return v


class UserUpdate(BaseModel):
    """Обновление пользователя (только Admin)."""

    role: RoleEnum | None = None
    is_active: bool | None = None
    password: str | None = None


class UserResponse(BaseModel):
    """Публичные данные пользователя."""

    id: int
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
