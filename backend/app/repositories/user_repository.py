"""
Репозиторий пользователей — наследует BaseRepository[User].
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """CRUD для модели User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """Найти пользователя по имени (регистронезависимо)."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """Количество всех пользователей (для seed первого Admin)."""
        return await self.count()
