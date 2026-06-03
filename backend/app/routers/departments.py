"""Роутер для справочника отделов."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Отделы"])


@router.get("", response_model=list[DepartmentResponse], summary="Список всех отделов")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Возвращает все отделы, отсортированные по имени."""
    service = DepartmentService(db)
    return await service.list_all()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, summary="Создать отдел")
async def create_department(
    body: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """Создаёт новый отдел. 409 если имя уже занято."""
    service = DepartmentService(db)
    return await service.create(body)


@router.put("/{dept_id}", response_model=DepartmentResponse, summary="Переименовать отдел")
async def update_department(
    dept_id: int,
    body: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """Переименовывает отдел. 404 если не найден, 409 если имя занято другим."""
    service = DepartmentService(db)
    return await service.update(dept_id, body)


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить отдел")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """Удаляет отдел. У исполнителей этого отдела department_id → NULL."""
    service = DepartmentService(db)
    await service.delete(dept_id)
