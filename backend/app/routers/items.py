"""Роутер для задач протокола совещания."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import PaginatedResponse, PriorityEnum, StateEnum
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["Задачи"])


@router.get("", response_model=PaginatedResponse[ItemResponse], summary="Список задач")
async def list_items(
    state: StateEnum | None = Query(None, description="Фильтр по состоянию"),
    search: str | None = Query(None, description="Поиск по теме и тикету"),
    executor_id: int | None = Query(None, description="Фильтр по исполнителю"),
    department_id: int | None = Query(None, description="Фильтр по отделу"),
    priority: PriorityEnum | None = Query(None, description="Фильтр по приоритету"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(1000, ge=1, le=5000, description="Размер страницы"),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает список задач с опциональной фильтрацией и пагинацией."""
    service = ItemService(db)
    return await service.list_items(
        state=state,
        search=search,
        executor_id=executor_id,
        department_id=department_id,
        priority=priority,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=ItemResponse, summary="Получить задачу")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает полные данные задачи по ID."""
    service = ItemService(db)
    return await service.get_item(item_id)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Создать задачу")
async def create_item(body: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт новую задачу, опционально с начальным статусом."""
    service = ItemService(db)
    return await service.create_item(body)


@router.patch("/{item_id}", response_model=ItemResponse, summary="Обновить задачу")
async def update_item(item_id: int, body: ItemUpdate, db: AsyncSession = Depends(get_db)):
    """Частично обновляет задачу (PATCH). Обновляются только переданные поля."""
    service = ItemService(db)
    return await service.update_item(item_id, body)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить задачу")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Удаляет задачу со всеми статусами и привязками к исполнителям."""
    service = ItemService(db)
    await service.delete_item(item_id)
