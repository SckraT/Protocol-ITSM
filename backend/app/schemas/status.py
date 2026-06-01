"""Схемы для истории статусов задачи."""
from datetime import date

from pydantic import BaseModel, ConfigDict


class StatusCreate(BaseModel):
    """Добавление новой записи статуса."""

    status_date: date | None = None
    status_note: str | None = None


class StatusResponse(BaseModel):
    """Ответ с данными статуса."""

    id: int
    item_id: int
    status_date: date | None
    status_note: str | None

    model_config = ConfigDict(from_attributes=True)
