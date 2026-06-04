"""Сервис для работы с исполнителями."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.executor import Executor
from app.repositories.department_repository import DepartmentRepository
from app.repositories.executor_repository import ExecutorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.executor import ExecutorResponse, ExecutorUpdate, ExecutorUserInfo, ExecutorCreate


def _to_response(executor: Executor) -> ExecutorResponse:
    """Формирует ExecutorResponse из ORM-объекта."""
    dept_name = executor.department.name if executor.department else None
    user_info = (
        ExecutorUserInfo(id=executor.user.id, username=executor.user.username)
        if executor.user else None
    )
    return ExecutorResponse(
        id=executor.id,
        name=executor.name,
        department_id=executor.department_id,
        department_name=dept_name,
        user_id=executor.user_id,
        user=user_info,
    )


class ExecutorService:
    """Бизнес-логика для исполнителей."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = ExecutorRepository(session)
        self.dept_repo = DepartmentRepository(session)
        self.user_repo = UserRepository(session)

    async def _check_user_free(self, user_id: int, executor_id: int | None) -> None:
        """Проверить, что УЗ существует и не занята другим исполнителем."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Учётная запись не найдена")
        if user.executor and user.executor.id != executor_id:
            raise HTTPException(status_code=409, detail="Учётная запись уже привязана к другому исполнителю")

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

        # Проверяем УЗ (если указана)
        if data.user_id is not None:
            await self._check_user_free(data.user_id, executor_id=None)

        executor = Executor(name=name, department_id=data.department_id, user_id=data.user_id)
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

        # Обновление привязки к УЗ (None — снять привязку)
        if "user_id" in data.model_fields_set:
            if data.user_id is not None:
                await self._check_user_free(data.user_id, executor_id=executor_id)
            executor.user_id = data.user_id

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
