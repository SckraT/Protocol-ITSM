"""
Сервис аутентификации: проверка учётных данных, выдача токенов, рефреш.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Сервис аутентификации и управления токенами."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def authenticate(self, identifier: str, password: str) -> TokenResponse | None:
        """
        Проверить учётные данные и вернуть токены.
        identifier — username, email или телефон (тип определяется автоматически).
        Возвращает None если пользователь не найден, заблокирован или пароль неверен.
        """
        user = await self.repo.get_by_identifier(identifier)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return self._build_token_response(user)

    async def refresh(self, refresh_token: str) -> TokenResponse | None:
        """
        Обновить access-токен по refresh-токену.
        Возвращает None если токен недействителен.
        """
        username = decode_refresh_token(refresh_token)
        if not username:
            return None
        user = await self.repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        return self._build_token_response(user)

    async def create_first_admin(self, username: str, password: str) -> User:
        """Создать первого Admin-пользователя (вызывается при пустой таблице users)."""
        user = User(
            username=username,
            hashed_password=hash_password(password),
            role=RoleEnum.admin,
            is_active=True,
        )
        return await self.repo.create(user)

    def _build_token_response(self, user: User) -> TokenResponse:
        """Собрать ответ с access и refresh токенами."""
        return TokenResponse(
            access_token=create_access_token(user.username, user.role),
            refresh_token=create_refresh_token(user.username),
            username=user.username,
            role=user.role,
            display_name=user.display_name,
        )
