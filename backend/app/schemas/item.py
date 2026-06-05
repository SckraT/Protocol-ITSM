"""Схемы для задач протокола."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.executor import Executor
from app.schemas.common import PriorityEnum, StateEnum


class ExecutorInItem(BaseModel):
    """Исполнитель в составе задачи (для ответа)."""

    id: int
    name: str
    department_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_executor(cls, executor: Executor) -> "ExecutorInItem":
        """Собрать из ORM-объекта Executor (с предзагруженным department)."""
        return cls(
            id=executor.id,
            name=executor.name,
            department_name=executor.department.name if executor.department else None,
        )


class StatusInItem(BaseModel):
    """Запись статуса в составе задачи (краткая форма)."""

    id: int
    status_date: date | None
    status_note: str | None

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    """Создание новой задачи."""

    topic: str = Field(..., min_length=1, description="Тема задачи")
    ticket: str | None = Field(None, max_length=100, description="Номер тикета (опционально)")
    priority: PriorityEnum | None = Field(None, description="Приоритет")
    state: StateEnum = Field(StateEnum.in_progress, description="Состояние задачи")
    due_date: date | None = Field(None, description="Срок выполнения")
    meeting_id: int | None = Field(None, description="ID совещания (опционально)")
    executor_ids: list[int] = Field(default_factory=list, description="ID исполнителей")
    # Начальный статус (опционально, добавляется вместе с задачей)
    status_date: date | None = Field(None, description="Дата начального статуса")
    status_note: str | None = Field(None, description="Примечание к начальному статусу")


class ItemUpdate(BaseModel):
    """Частичное обновление задачи (PATCH)."""

    topic: str | None = Field(None, min_length=1, description="Тема задачи")
    ticket: str | None = Field(None, max_length=100)
    priority: PriorityEnum | None = None
    state: StateEnum | None = None
    due_date: date | None = None
    meeting_id: int | None = Field(None, description="ID совещания (null — отвязать)")
    executor_ids: list[int] | None = Field(None, description="Новый список ID исполнителей")


class ItemResponse(BaseModel):
    """Полный ответ с данными задачи."""

    id: int
    topic: str
    ticket: str | None
    priority: PriorityEnum | None
    state: StateEnum
    due_date: date | None
    meeting_id: int | None = None
    meeting_title: str | None = None
    created_at: datetime
    executors: list[ExecutorInItem] = []
    recent_statuses: list[StatusInItem] = []
    status_count: int = 0

    model_config = ConfigDict(from_attributes=True)
