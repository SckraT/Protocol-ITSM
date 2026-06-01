"""
Базовый generic-репозиторий с CRUD-операциями.
Все конкретные репозитории наследуются от BaseRepository[T].
"""
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с типовыми CRUD-операциями."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, id: int) -> ModelType | None:
        """Получить запись по первичному ключу."""
        return await self.session.get(self.model, id)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Получить список всех записей с пагинацией."""
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """Сохранить новый объект в БД. Flush — для получения ID без commit."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Удалить объект из БД."""
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self) -> int:
        """Подсчитать количество записей в таблице."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
