"""
Репозиторий для работы с задачами протокола.
Включает фильтрацию, поиск и загрузку связанных сущностей.
"""
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.executor import Executor
from app.models.item import Item
from app.models.item_executor import item_executor_table
from app.repositories.base import BaseRepository
from app.schemas.common import PriorityEnum, StateEnum


class ItemRepository(BaseRepository[Item]):
    """Репозиторий задач с поддержкой фильтрации и загрузки связей."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Item, session)

    def _base_query(self):
        """Базовый запрос с предзагрузкой связанных объектов."""
        return (
            select(Item)
            .options(
                # Предзагружаем исполнителей вместе с их отделами
                selectinload(Item.executors).selectinload(Executor.department),
                # Предзагружаем все статусы
                selectinload(Item.statuses),
                # Предзагружаем совещание (для meeting_title)
                selectinload(Item.meeting),
            )
            .order_by(Item.id)
        )

    async def get_with_relations(self, item_id: int) -> Item | None:
        """Получить задачу с предзагруженными исполнителями и статусами."""
        result = await self.session.execute(
            self._base_query().where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        state: StateEnum | None = None,
        search: str | None = None,
        executor_id: int | None = None,
        department_id: int | None = None,
        priority: PriorityEnum | None = None,
        meeting_id: int | None = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[Sequence[Item], int]:
        """
        Получить список задач с фильтрацией и общее количество.
        Возвращает кортеж (список задач, всего записей).
        """
        # Базовый запрос
        stmt = self._base_query()
        count_stmt = select(func.count()).select_from(Item)

        # Фильтр по состоянию
        if state is not None:
            stmt = stmt.where(Item.state == state.value)
            count_stmt = count_stmt.where(Item.state == state.value)

        # Фильтр по приоритету
        if priority is not None:
            stmt = stmt.where(Item.priority == priority.value)
            count_stmt = count_stmt.where(Item.priority == priority.value)

        # Фильтр по совещанию (0 — задачи без совещания)
        if meeting_id is not None:
            if meeting_id == 0:
                stmt = stmt.where(Item.meeting_id.is_(None))
                count_stmt = count_stmt.where(Item.meeting_id.is_(None))
            else:
                stmt = stmt.where(Item.meeting_id == meeting_id)
                count_stmt = count_stmt.where(Item.meeting_id == meeting_id)

        # Полнотекстовый поиск по теме и тикету
        if search:
            search_pattern = f"%{search}%"
            search_filter = or_(
                Item.topic.ilike(search_pattern),
                Item.ticket.ilike(search_pattern),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        # Фильтр по исполнителю (через M2M)
        if executor_id is not None:
            executor_filter = Item.id.in_(
                select(item_executor_table.c.item_id).where(
                    item_executor_table.c.executor_id == executor_id
                )
            )
            stmt = stmt.where(executor_filter)
            count_stmt = count_stmt.where(executor_filter)

        # Фильтр по отделу (через исполнителей)
        if department_id is not None:
            dept_filter = Item.id.in_(
                select(item_executor_table.c.item_id)
                .join(Executor, Executor.id == item_executor_table.c.executor_id)
                .where(Executor.department_id == department_id)
            )
            stmt = stmt.where(dept_filter)
            count_stmt = count_stmt.where(dept_filter)

        # Получаем общее количество
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        # Применяем пагинацию
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return items, total

    async def update_executors(self, item: Item, executor_ids: list[int]) -> None:
        """Обновить список исполнителей задачи."""
        from app.models.executor import Executor as ExecutorModel

        # Загружаем исполнителей по ID
        if executor_ids:
            result = await self.session.execute(
                select(ExecutorModel).where(ExecutorModel.id.in_(executor_ids))
            )
            new_executors = list(result.scalars().all())
        else:
            new_executors = []

        # Заменяем коллекцию исполнителей
        item.executors = new_executors
        await self.session.flush()
