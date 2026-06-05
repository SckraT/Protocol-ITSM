"""Роутер для справочника исполнителей."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.executor import ExecutorCreate, ExecutorResponse, ExecutorUpdate, ExecutorUserInfo
from app.services.executor_service import ExecutorService

router = APIRouter(prefix="/executors", tags=["Исполнители"])


@router.get("", response_model=list[ExecutorResponse], summary="Список всех исполнителей")
async def list_executors(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[ExecutorResponse]:
    """Возвращает всех исполнителей с именами отделов."""
    service = ExecutorService(db)
    return await service.list_all()


@router.get("/user-options", response_model=list[ExecutorUserInfo], summary="Список УЗ для привязки")
async def user_options(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> list[ExecutorUserInfo]:
    """Краткий список учётных записей (id + username) для выбора привязки. Доступно editor."""
    repo = UserRepository(db)
    users = await repo.list(limit=1000)
    return [ExecutorUserInfo(id=u.id, username=u.username) for u in users]


@router.post("", response_model=ExecutorResponse, status_code=status.HTTP_201_CREATED, summary="Создать исполнителя")
async def create_executor(
    body: ExecutorCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> ExecutorResponse:
    """Создаёт нового исполнителя. 409 если имя занято."""
    service = ExecutorService(db)
    return await service.create(body)


@router.put("/{executor_id}", response_model=ExecutorResponse, summary="Обновить исполнителя")
async def update_executor(
    executor_id: int,
    body: ExecutorUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> ExecutorResponse:
    """Обновляет имя и/или отдел исполнителя."""
    service = ExecutorService(db)
    return await service.update(executor_id, body)


@router.delete("/{executor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить исполнителя")
async def delete_executor(
    executor_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
) -> None:
    """Удаляет исполнителя из справочника."""
    service = ExecutorService(db)
    await service.delete(executor_id)
