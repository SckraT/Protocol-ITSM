"""
Сервис для работы с совещаниями: сериализация и CRUD.
"""
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.models.meeting import Meeting
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.common import PaginatedResponse
from app.schemas.item import ExecutorInItem
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate


def _serialize_meeting(meeting: Meeting, item_count: int) -> MeetingResponse:
    """Собрать MeetingResponse из ORM-объекта (участники + счётчик задач)."""
    participants = [ExecutorInItem.from_executor(e) for e in meeting.participants]
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        meeting_date=meeting.meeting_date,
        description=meeting.description,
        created_at=meeting.created_at,
        participants=participants,
        item_count=item_count,
    )


class MeetingService:
    """Бизнес-логика для совещаний."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = MeetingRepository(session)

    async def list_meetings(
        self,
        search: str | None = None,
        page: int = 1,
        page_size: int = 1000,
    ) -> PaginatedResponse[MeetingResponse]:
        """Получить список совещаний с поиском и пагинацией."""
        offset = (page - 1) * page_size
        meetings, total = await self.repo.list_with_filters(
            search=search,
            offset=offset,
            limit=page_size,
        )
        counts = await self.repo.item_counts([m.id for m in meetings])
        return PaginatedResponse(
            items=[_serialize_meeting(m, counts.get(m.id, 0)) for m in meetings],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_meeting(self, meeting_id: int) -> MeetingResponse:
        """Получить совещание по ID. 404 если не найдено."""
        meeting = await self.repo.get_with_relations(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Совещание не найдено")
        counts = await self.repo.item_counts([meeting_id])
        return _serialize_meeting(meeting, counts.get(meeting_id, 0))

    async def create_meeting(self, data: MeetingCreate) -> MeetingResponse:
        """Создать новое совещание."""
        meeting = Meeting(
            title=data.title,
            meeting_date=data.meeting_date,
            description=data.description,
        )
        created = await self.repo.create(meeting)

        if data.participant_ids:
            await self.repo.update_participants(created, data.participant_ids)

        meeting_with_relations = await self.repo.get_with_relations(created.id)
        # Новое совещание ещё не имеет задач — item_count=0 без запроса.
        return _serialize_meeting(meeting_with_relations, 0)  # type: ignore[arg-type]

    async def update_meeting(self, meeting_id: int, data: MeetingUpdate) -> MeetingResponse:
        """Частичное обновление совещания (PATCH). 404 если не найдено."""
        meeting = await self.repo.get_with_relations(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Совещание не найдено")

        update_data = data.model_dump(exclude_unset=True)
        participant_ids = update_data.pop("participant_ids", None)

        for field, value in update_data.items():
            setattr(meeting, field, value)

        if participant_ids is not None:
            await self.repo.update_participants(meeting, participant_ids)

        await self.repo.session.flush()

        updated = await self.repo.get_with_relations(meeting_id)
        counts = await self.repo.item_counts([meeting_id])
        return _serialize_meeting(updated, counts.get(meeting_id, 0))  # type: ignore[arg-type]

    async def delete_meeting(self, meeting_id: int) -> None:
        """
        Удалить совещание. У привязанных задач meeting_id обнуляется явно —
        надёжно и на SQLite, где FK-констрейнт мог не примениться через ALTER.
        """
        meeting = await self.repo.get(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Совещание не найдено")
        # Снимаем привязку у задач одним UPDATE (не загружая их строки)
        await self.repo.session.execute(
            update(Item).where(Item.meeting_id == meeting_id).values(meeting_id=None)
        )
        await self.repo.session.flush()
        await self.repo.delete(meeting)
