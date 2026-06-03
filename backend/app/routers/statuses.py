"""Роутер для истории статусов задач."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.schemas.status import StatusCreate, StatusResponse
from app.services.status_service import StatusService

router = APIRouter(tags=["Статусы"])


@router.get("/items/{item_id}/statuses", response_model=list[StatusResponse], summary="История статусов задачи")
async def list_statuses(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Возвращает все статусы задачи в обратном хронологическом порядке."""
    service = StatusService(db)
    return await service.list_for_item(item_id)


@router.post(
    "/items/{item_id}/statuses",
    response_model=StatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить статус к задаче",
)
async def add_status(
    item_id: int,
    body: StatusCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """Добавляет новую запись в историю статусов задачи."""
    service = StatusService(db)
    return await service.add(item_id, body)


@router.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить запись статуса")
async def delete_status(
    status_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """Удаляет одну запись из истории статусов."""
    service = StatusService(db)
    await service.delete(status_id)
