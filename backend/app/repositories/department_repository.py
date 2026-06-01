"""Репозиторий для работы с отделами."""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Репозиторий отделов."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Department, session)

    async def get_all(self) -> Sequence[Department]:
        """Получить все отделы, отсортированные по имени."""
        result = await self.session.execute(
            select(Department).order_by(Department.name)
        )
        return result.scalars().all()

    async def get_by_name(self, name: str) -> Department | None:
        """Найти отдел по точному названию."""
        result = await self.session.execute(
            select(Department).where(Department.name == name)
        )
        return result.scalar_one_or_none()
