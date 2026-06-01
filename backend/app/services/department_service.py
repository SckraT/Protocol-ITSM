"""Сервис для работы с отделами."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate


class DepartmentService:
    """Бизнес-логика для отделов."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = DepartmentRepository(session)

    async def list_all(self) -> list[DepartmentResponse]:
        """Получить все отделы."""
        departments = await self.repo.get_all()
        return [DepartmentResponse.model_validate(d) for d in departments]

    async def create(self, data: DepartmentCreate) -> DepartmentResponse:
        """Создать отдел. 409 если имя уже занято."""
        name = data.name.strip()
        existing = await self.repo.get_by_name(name)
        if existing:
            raise HTTPException(status_code=409, detail="Отдел с таким именем уже существует")

        dept = Department(name=name)
        created = await self.repo.create(dept)
        return DepartmentResponse.model_validate(created)

    async def update(self, dept_id: int, data: DepartmentUpdate) -> DepartmentResponse:
        """Переименовать отдел. 404 если не найден, 409 если имя занято."""
        dept = await self.repo.get(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Отдел не найден")

        name = data.name.strip()
        existing = await self.repo.get_by_name(name)
        if existing and existing.id != dept_id:
            raise HTTPException(status_code=409, detail="Отдел с таким именем уже существует")

        dept.name = name
        await self.repo.session.flush()
        return DepartmentResponse.model_validate(dept)

    async def delete(self, dept_id: int) -> None:
        """Удалить отдел. При удалении department_id у исполнителей → NULL (через FK ON DELETE SET NULL)."""
        dept = await self.repo.get(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Отдел не найден")
        await self.repo.delete(dept)
