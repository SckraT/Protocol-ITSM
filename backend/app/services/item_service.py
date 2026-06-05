"""
Сервис для работы с задачами протокола.
Содержит бизнес-логику: сериализацию, обновление, удаление.
"""
from datetime import date as date_type

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.models.meeting import Meeting
from app.models.status import Status
from app.repositories.item_repository import ItemRepository
from app.repositories.status_repository import StatusRepository
from app.schemas.common import PaginatedResponse, PriorityEnum, StateEnum
from app.schemas.item import ExecutorInItem, ItemCreate, ItemResponse, ItemUpdate, StatusInItem


def _serialize_item(item: Item) -> ItemResponse:
    """
    Собирает ItemResponse из ORM-объекта.
    Включает: 3 последних статуса, полные данные исполнителей, счётчик статусов.
    Повторяет логику serialize_item() из v1.
    """
    # Сортировка статусов: сначала самые свежие (date.min для NULL дат)
    sorted_statuses = sorted(
        item.statuses,
        key=lambda s: (s.status_date or date_type.min, s.id),
        reverse=True,
    )
    recent_statuses = [
        StatusInItem(
            id=s.id,
            status_date=s.status_date,
            status_note=s.status_note,
        )
        for s in sorted_statuses[:3]
    ]

    # Список исполнителей с именами отделов
    executors = [ExecutorInItem.from_executor(e) for e in item.executors]

    return ItemResponse(
        id=item.id,
        topic=item.topic,
        ticket=item.ticket,
        priority=PriorityEnum(item.priority) if item.priority else None,
        state=StateEnum(item.state),
        due_date=item.due_date,
        meeting_id=item.meeting_id,
        meeting_title=item.meeting.title if item.meeting else None,
        created_at=item.created_at,
        executors=executors,
        recent_statuses=recent_statuses,
        status_count=len(item.statuses),
    )


class ItemService:
    """Бизнес-логика для задач протокола."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = ItemRepository(session)
        self.status_repo = StatusRepository(session)

    async def _ensure_meeting_exists(self, meeting_id: int | None) -> None:
        """Проверить, что совещание существует (400 если нет). None — пропускаем."""
        if meeting_id is None:
            return
        result = await self.repo.session.execute(
            select(Meeting.id).where(Meeting.id == meeting_id)
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=400, detail="Указанное совещание не существует")

    async def list_items(
        self,
        state: StateEnum | None = None,
        search: str | None = None,
        executor_id: int | None = None,
        department_id: int | None = None,
        priority: PriorityEnum | None = None,
        meeting_id: int | None = None,
        page: int = 1,
        page_size: int = 1000,
    ) -> PaginatedResponse[ItemResponse]:
        """Получить список задач с фильтрацией и пагинацией."""
        offset = (page - 1) * page_size
        items, total = await self.repo.list_with_filters(
            state=state,
            search=search,
            executor_id=executor_id,
            department_id=department_id,
            priority=priority,
            meeting_id=meeting_id,
            offset=offset,
            limit=page_size,
        )
        return PaginatedResponse(
            items=[_serialize_item(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_item(self, item_id: int) -> ItemResponse:
        """Получить задачу по ID. 404 если не найдена."""
        item = await self.repo.get_with_relations(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return _serialize_item(item)

    async def create_item(self, data: ItemCreate) -> ItemResponse:
        """Создать новую задачу, опционально с начальным статусом."""
        await self._ensure_meeting_exists(data.meeting_id)
        item = Item(
            topic=data.topic,
            ticket=data.ticket,
            priority=data.priority.value if data.priority else None,
            state=data.state.value,
            due_date=data.due_date,
            meeting_id=data.meeting_id,
        )
        created = await self.repo.create(item)

        # Устанавливаем исполнителей
        if data.executor_ids:
            await self.repo.update_executors(created, data.executor_ids)

        # Создаём начальный статус, если указан
        if data.status_note or data.status_date:
            status = Status(
                item_id=created.id,
                status_date=data.status_date,
                status_note=data.status_note,
            )
            await self.status_repo.create(status)
            # Точечно сбрасываем коллекцию statuses созданной задачи: она была загружена
            # пустой до создания статуса. expire только этой связи (не expire_all — иначе
            # ленивая подгрузка прочих атрибутов в async-контексте даёт MissingGreenlet).
            self.repo.session.expire(created, ["statuses"])

        # Перезагружаем с полными связями
        item_with_relations = await self.repo.get_with_relations(created.id)
        return _serialize_item(item_with_relations)  # type: ignore[arg-type]

    async def update_item(self, item_id: int, data: ItemUpdate) -> ItemResponse:
        """Частичное обновление задачи (PATCH). 404 если не найдена."""
        item = await self.repo.get_with_relations(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        # Обновляем только переданные поля
        update_data = data.model_dump(exclude_unset=True)
        executor_ids = update_data.pop("executor_ids", None)

        # Привязка к совещанию: значение (не None) должно ссылаться на существующее
        if "meeting_id" in update_data:
            await self._ensure_meeting_exists(update_data["meeting_id"])

        for field, value in update_data.items():
            if field == "priority":
                setattr(item, field, value.value if value else None)
            elif field == "state":
                setattr(item, field, value.value if value else item.state)
            else:
                setattr(item, field, value)

        # Обновляем исполнителей если они переданы
        if executor_ids is not None:
            await self.repo.update_executors(item, executor_ids)

        await self.repo.session.flush()

        # Если менялась привязка к совещанию — сбрасываем закешированное отношение,
        # чтобы selectinload при перезагрузке подтянул актуальное meeting (и meeting_title).
        if "meeting_id" in update_data:
            self.repo.session.expire(item, ["meeting"])

        # Перезагружаем с обновлёнными связями
        updated = await self.repo.get_with_relations(item_id)
        return _serialize_item(updated)  # type: ignore[arg-type]

    async def delete_item(self, item_id: int) -> None:
        """Удалить задачу (каскадно удаляет статусы и связи с исполнителями)."""
        item = await self.repo.get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        await self.repo.delete(item)
