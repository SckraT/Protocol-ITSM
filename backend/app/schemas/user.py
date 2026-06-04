"""
Pydantic-схемы для управления пользователями (Admin-панель).
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import RoleEnum
from app.utils.identifiers import normalize_phone


def _normalize_phone_or_none(v: str | None) -> str | None:
    """Нормализовать телефон; пустую строку привести к None."""
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    return normalize_phone(v)


def _empty_email_to_none(v: str | None) -> str | None:
    """Привести email к нижнему регистру; пустую строку — к None.
    Нижний регистр обязателен: поиск по email тоже идёт в lower (см. UserRepository)."""
    if v is None:
        return None
    v = v.strip().lower()
    return v or None


class UserCreate(BaseModel):
    """Создание нового пользователя."""

    username: str
    password: str
    role: RoleEnum = RoleEnum.viewer
    email: EmailStr | None = None
    phone: str | None = None

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

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v: str | None) -> str | None:
        return _empty_email_to_none(v)

    @field_validator("phone")
    @classmethod
    def normalize_phone_field(cls, v: str | None) -> str | None:
        return _normalize_phone_or_none(v)


class UserUpdate(BaseModel):
    """Обновление пользователя (только Admin)."""

    role: RoleEnum | None = None
    is_active: bool | None = None
    password: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v: str | None) -> str | None:
        return _empty_email_to_none(v)

    @field_validator("phone")
    @classmethod
    def normalize_phone_field(cls, v: str | None) -> str | None:
        return _normalize_phone_or_none(v)


class UserResponse(BaseModel):
    """Публичные данные пользователя."""

    id: int
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    email: str | None = None
    phone: str | None = None
    executor_id: int | None = None  # читается из property User.executor_id

    model_config = {"from_attributes": True}
