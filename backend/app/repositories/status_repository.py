"""Репозиторий для работы с историей статусов задач."""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.status import Status
from app.repositories.base import BaseRepository


class StatusRepository(BaseRepository[Status]):
    """Репозиторий статусов задачи."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Status, session)

    async def get_all_for_item(self, item_id: int) -> Sequence[Status]:
        """Получить все статусы задачи в обратном хронологическом порядке."""
        result = await self.session.execute(
            select(Status)
            .where(Status.item_id == item_id)
            .order_by(Status.status_date.desc().nullslast(), Status.id.desc())
        )
        return result.scalars().all()
