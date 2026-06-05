"""
Pydantic-схемы для аутентификации: запросы и ответы.
"""
from pydantic import BaseModel, Field, field_validator

from app.models.user import RoleEnum


class LoginRequest(BaseModel):
    """Запрос на вход: идентификатор (username/email/телефон) + пароль."""

    # max_length ограничивает размер входа, чтобы не дать атакующему раздувать
    # логи/сторедж попытками брутфорса с мегабайтными строками.
    identifier: str = Field(..., max_length=255, description="Логин, email или телефон")
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Ответ с JWT-токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: RoleEnum
    display_name: str
    must_change_password: bool = False


class RefreshRequest(BaseModel):
    """Запрос обновления токена."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Запрос смены собственного пароля."""

    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Новый пароль должен содержать минимум 8 символов")
        return v


class MeResponse(BaseModel):
    """Информация о текущем пользователе."""

    id: int
    username: str
    role: RoleEnum
    is_active: bool
    display_name: str
    must_change_password: bool = False
