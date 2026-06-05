"""Репозиторий для работы с исполнителями."""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.department import Department
from app.models.executor import Executor
from app.repositories.base import BaseRepository


class ExecutorRepository(BaseRepository[Executor]):
    """Репозиторий исполнителей."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Executor, session)

    async def get_all(self) -> Sequence[Executor]:
        """Получить всех исполнителей с их отделами.
        Сортировка: сначала по отделу (NULL — в конце), затем по имени исполнителя.
        Повторяет порядок сортировки из v1 (ORDER BY d.name, e.name).
        """
        result = await self.session.execute(
            select(Executor)
            .outerjoin(Executor.department)
            .options(selectinload(Executor.department))
            .order_by(Department.name.nullslast(), Executor.name)
        )
        return result.scalars().all()

    async def get_by_ids(self, ids: list[int]) -> Sequence[Executor]:
        """Получить исполнителей по списку ID."""
        if not ids:
            return []
        result = await self.session.execute(
            select(Executor)
            .options(selectinload(Executor.department))
            .where(Executor.id.in_(ids))
        )
        return result.scalars().all()

    async def get_by_name(self, name: str) -> Executor | None:
        """Найти исполнителя по точному имени."""
        result = await self.session.execute(
            select(Executor)
            .options(selectinload(Executor.department))
            .where(Executor.name == name)
        )
        return result.scalar_one_or_none()
