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
        """Создать первого Admin-пользователя (вызывается при пустой таблице users).
        must_change_password=True — заставляет сменить дефолтный пароль при первом входе."""
        user = User(
            username=username,
            hashed_password=hash_password(password),
            role=RoleEnum.admin,
            is_active=True,
            must_change_password=True,
        )
        return await self.repo.create(user)

    async def change_password(self, user: User, old_password: str, new_password: str) -> None:
        """Сменить пароль текущего пользователя. Проверяет старый пароль."""
        if not verify_password(old_password, user.hashed_password):
            raise ValueError("Неверный текущий пароль")
        if len(new_password) < 8:
            raise ValueError("Новый пароль должен содержать минимум 8 символов")
        user.hashed_password = hash_password(new_password)
        user.must_change_password = False
        await self.repo.session.flush()

    def _build_token_response(self, user: User) -> TokenResponse:
        """Собрать ответ с access и refresh токенами."""
        return TokenResponse(
            access_token=create_access_token(user.username, user.role),
            refresh_token=create_refresh_token(user.username),
            username=user.username,
            role=RoleEnum(user.role),
            display_name=user.display_name,
            must_change_password=user.must_change_password,
        )
