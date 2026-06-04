"""
Pydantic-схемы для аутентификации: запросы и ответы.
"""
from pydantic import BaseModel

from app.models.user import RoleEnum


class LoginRequest(BaseModel):
    """Запрос на вход: идентификатор (username/email/телефон) + пароль."""

    identifier: str
    password: str


class TokenResponse(BaseModel):
    """Ответ с JWT-токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: RoleEnum
    display_name: str


class RefreshRequest(BaseModel):
    """Запрос обновления токена."""

    refresh_token: str


class MeResponse(BaseModel):
    """Информация о текущем пользователе."""

    id: int
    username: str
    role: RoleEnum
    is_active: bool
    display_name: str
