"""
Репозиторий пользователей — наследует BaseRepository[User].
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository
from app.utils.identifiers import detect_identifier


class UserRepository(BaseRepository[User]):
    """CRUD для модели User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """Найти пользователя по имени (регистронезависимо)."""
        result = await self.session.execute(
            select(User).where(func.lower(User.username) == username.strip().lower())
        )
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Найти пользователя по username, email или телефону (тип определяется автоматически)."""
        kind, value = detect_identifier(identifier)
        if kind == "email":
            col = User.email
        elif kind == "phone":
            col = User.phone
        else:
            col = func.lower(User.username)
        result = await self.session.execute(select(User).where(col == value))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email (для проверки уникальности)."""
        result = await self.session.execute(
            select(User).where(User.email == email.strip().lower())
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Найти пользователя по телефону (для проверки уникальности)."""
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Количество всех пользователей (для seed первого Admin)."""
        return await self.count()
