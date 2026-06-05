"""Роутер для совещаний."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/meetings", tags=["Совещания"])


@router.get("", response_model=PaginatedResponse[MeetingResponse], summary="Список совещаний")
async def list_meetings(
    search: str | None = Query(None, description="Поиск по теме"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(1000, ge=1, le=5000, description="Размер страницы"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> PaginatedResponse[MeetingResponse]:
    """Возвращает список совещаний с опциональным поиском и пагинацией."""
    service = MeetingService(db)
    return await service.list_meetings(search=search, page=page, page_size=page_size)


@router.get("/{meeting_id}", response_model=MeetingResponse, summary="Получить совещание")
async def get_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> MeetingResponse:
    """Возвращает совещание по ID."""
    service = MeetingService(db)
    return await service.get_meeting(meeting_id)


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED, summary="Создать совещание")
async def create_meeting(
    body: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> MeetingResponse:
    """Создаёт новое совещание с участниками."""
    service = MeetingService(db)
    return await service.create_meeting(body)


@router.patch("/{meeting_id}", response_model=MeetingResponse, summary="Обновить совещание")
async def update_meeting(
    meeting_id: int,
    body: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> MeetingResponse:
    """Частично обновляет совещание (PATCH)."""
    service = MeetingService(db)
    return await service.update_meeting(meeting_id, body)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить совещание")
async def delete_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> None:
    """Удаляет совещание. Привязка задач сбрасывается (meeting_id → null)."""
    service = MeetingService(db)
    await service.delete_meeting(meeting_id)
