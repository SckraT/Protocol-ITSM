"""Схемы для совещаний."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item import ExecutorInItem


class MeetingCreate(BaseModel):
    """Создание совещания."""

    title: str = Field(..., min_length=1, description="Тема совещания")
    meeting_date: date | None = Field(None, description="Дата совещания")
    description: str | None = Field(None, description="Заметки / протокол")
    participant_ids: list[int] = Field(default_factory=list, description="ID участников (исполнителей)")


class MeetingUpdate(BaseModel):
    """Частичное обновление совещания (PATCH)."""

    title: str | None = Field(None, min_length=1)
    meeting_date: date | None = None
    description: str | None = None
    participant_ids: list[int] | None = Field(None, description="Новый список ID участников")


class MeetingResponse(BaseModel):
    """Полный ответ с данными совещания."""

    id: int
    title: str
    meeting_date: date | None
    description: str | None
    created_at: datetime
    participants: list[ExecutorInItem] = []
    item_count: int = 0

    model_config = ConfigDict(from_attributes=True)
