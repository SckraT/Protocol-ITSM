"""Схемы для исполнителей."""
from pydantic import BaseModel, ConfigDict, Field


class ExecutorCreate(BaseModel):
    """Создание нового исполнителя."""

    name: str = Field(..., min_length=1, max_length=255, description="Имя исполнителя")
    department_id: int | None = Field(None, description="ID отдела (опционально)")


class ExecutorUpdate(BaseModel):
    """Обновление исполнителя."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Новое имя")
    department_id: int | None = Field(None, description="Новый отдел (None = без отдела)")


class ExecutorResponse(BaseModel):
    """Ответ с данными исполнителя."""

    id: int
    name: str
    department_id: int | None
    department_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
