"""Сервис для работы с историей статусов задач."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.status import Status
from app.repositories.item_repository import ItemRepository
from app.repositories.status_repository import StatusRepository
from app.schemas.status import StatusCreate, StatusResponse


class StatusService:
    """Бизнес-логика для статусов задачи."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = StatusRepository(session)
        self.item_repo = ItemRepository(session)

    async def list_for_item(self, item_id: int) -> list[StatusResponse]:
        """Получить все статусы задачи в обратном хронологическом порядке."""
        item = await self.item_repo.get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        statuses = await self.repo.get_all_for_item(item_id)
        return [StatusResponse.model_validate(s) for s in statuses]

    async def add(self, item_id: int, data: StatusCreate) -> StatusResponse:
        """Добавить запись статуса к задаче."""
        item = await self.item_repo.get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        status = Status(
            item_id=item_id,
            status_date=data.status_date,
            status_note=data.status_note,
        )
        created = await self.repo.create(status)
        return StatusResponse.model_validate(created)

    async def delete(self, status_id: int) -> None:
        """Удалить запись статуса."""
        status = await self.repo.get(status_id)
        if not status:
            raise HTTPException(status_code=404, detail="Статус не найден")
        await self.repo.delete(status)
