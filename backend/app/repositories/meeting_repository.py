"""
Репозиторий для работы с совещаниями.
Загрузка участников (с отделами) и задач для счётчика.
"""
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.executor import Executor
from app.models.item import Item
from app.models.meeting import Meeting
from app.repositories.base import BaseRepository


class MeetingRepository(BaseRepository[Meeting]):
    """Репозиторий совещаний с загрузкой связей."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Meeting, session)

    def _base_query(self):
        """Базовый запрос с предзагрузкой участников (и их отделов)."""
        return (
            select(Meeting)
            .options(
                selectinload(Meeting.participants).selectinload(Executor.department),
            )
            .order_by(Meeting.meeting_date.desc().nullslast(), Meeting.id.desc())
        )

    async def item_counts(self, meeting_ids: Sequence[int]) -> dict[int, int]:
        """Кол-во задач по каждому совещанию одним GROUP BY (вместо загрузки строк)."""
        if not meeting_ids:
            return {}
        result = await self.session.execute(
            select(Item.meeting_id, func.count())
            .where(Item.meeting_id.in_(meeting_ids))
            .group_by(Item.meeting_id)
        )
        return {mid: cnt for mid, cnt in result.all()}

    async def get_with_relations(self, meeting_id: int) -> Meeting | None:
        """Получить совещание с предзагруженными участниками и задачами."""
        result = await self.session.execute(
            self._base_query().where(Meeting.id == meeting_id)
        )
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        search: str | None = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[Sequence[Meeting], int]:
        """Получить список совещаний с поиском по теме и общее количество."""
        stmt = self._base_query()
        count_stmt = select(func.count()).select_from(Meeting)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(Meeting.title.ilike(search_pattern))
            count_stmt = count_stmt.where(Meeting.title.ilike(search_pattern))

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        meetings = result.scalars().all()

        return meetings, total

    async def update_participants(self, meeting: Meeting, participant_ids: list[int]) -> None:
        """Обновить список участников совещания."""
        if participant_ids:
            result = await self.session.execute(
                select(Executor).where(Executor.id.in_(participant_ids))
            )
            new_participants = list(result.scalars().all())
        else:
            new_participants = []

        meeting.participants = new_participants
        await self.session.flush()
