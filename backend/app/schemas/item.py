"""Схемы для задач протокола."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PriorityEnum, StateEnum


class ExecutorInItem(BaseModel):
    """Исполнитель в составе задачи (для ответа)."""

    id: int
    name: str
    department_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


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
    executor_ids: list[int] | None = Field(None, description="Новый список ID исполнителей")


class ItemResponse(BaseModel):
    """Полный ответ с данными задачи."""

    id: int
    topic: str
    ticket: str | None
    priority: PriorityEnum | None
    state: StateEnum
    due_date: date | None
    created_at: datetime
    executors: list[ExecutorInItem] = []
    recent_statuses: list[StatusInItem] = []
    status_count: int = 0

    model_config = ConfigDict(from_attributes=True)
