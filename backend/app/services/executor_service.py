"""Сервис для работы с исполнителями."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.executor import Executor
from app.repositories.department_repository import DepartmentRepository
from app.repositories.executor_repository import ExecutorRepository
from app.schemas.executor import ExecutorCreate, ExecutorResponse, ExecutorUpdate


def _to_response(executor: Executor) -> ExecutorResponse:
    """Формирует ExecutorResponse из ORM-объекта."""
    dept_name = executor.department.name if executor.department else None
    return ExecutorResponse(
        id=executor.id,
        name=executor.name,
        department_id=executor.department_id,
        department_name=dept_name,
    )


class ExecutorService:
    """Бизнес-логика для исполнителей."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = ExecutorRepository(session)
        self.dept_repo = DepartmentRepository(session)

    async def list_all(self) -> list[ExecutorResponse]:
        """Получить всех исполнителей с именами отделов."""
        executors = await self.repo.get_all()
        return [_to_response(e) for e in executors]

    async def create(self, data: ExecutorCreate) -> ExecutorResponse:
        """Создать исполнителя. 409 если имя занято, 404 если отдел не найден."""
        name = data.name.strip()
        existing = await self.repo.get_by_name(name)
        if existing:
            raise HTTPException(status_code=409, detail="Исполнитель с таким именем уже существует")

        # Проверяем существование отдела (если указан)
        if data.department_id is not None:
            dept = await self.dept_repo.get(data.department_id)
            if not dept:
                raise HTTPException(status_code=404, detail="Отдел не найден")

        executor = Executor(name=name, department_id=data.department_id)
        created = await self.repo.create(executor)
        # Перезагружаем с отделом
        refreshed = await self.repo.get_by_name(created.name)
        return _to_response(refreshed)  # type: ignore[arg-type]

    async def update(self, executor_id: int, data: ExecutorUpdate) -> ExecutorResponse:
        """Обновить имя и/или отдел исполнителя."""
        executor = await self.repo.get(executor_id)
        if not executor:
            raise HTTPException(status_code=404, detail="Исполнитель не найден")

        # Проверка уникальности нового имени
        if data.name is not None:
            name = data.name.strip()
            existing = await self.repo.get_by_name(name)
            if existing and existing.id != executor_id:
                raise HTTPException(status_code=409, detail="Исполнитель с таким именем уже существует")
            executor.name = name

        # Обновление отдела (None — убрать привязку к отделу)
        if "department_id" in data.model_fields_set:
            if data.department_id is not None:
                dept = await self.dept_repo.get(data.department_id)
                if not dept:
                    raise HTTPException(status_code=404, detail="Отдел не найден")
            executor.department_id = data.department_id

        await self.repo.session.flush()
        # Перезагружаем с обновлённым отделом
        refreshed = await self.repo.get(executor_id)
        return _to_response(refreshed)  # type: ignore[arg-type]

    async def delete(self, executor_id: int) -> None:
        """Удалить исполнителя из справочника."""
        executor = await self.repo.get(executor_id)
        if not executor:
            raise HTTPException(status_code=404, detail="Исполнитель не найден")
        await self.repo.delete(executor)
