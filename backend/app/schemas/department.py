"""Схемы для отделов."""
from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    """Создание нового отдела."""

    name: str = Field(..., min_length=1, max_length=255, description="Название отдела")


class DepartmentUpdate(BaseModel):
    """Обновление отдела."""

    name: str = Field(..., min_length=1, max_length=255, description="Новое название отдела")


class DepartmentResponse(BaseModel):
    """Ответ с данными отдела."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
