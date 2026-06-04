"""Схемы для исполнителей."""
from pydantic import BaseModel, ConfigDict, Field


class ExecutorUserInfo(BaseModel):
    """Краткая информация о привязанной учётной записи."""

    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class ExecutorCreate(BaseModel):
    """Создание нового исполнителя."""

    name: str = Field(..., min_length=1, max_length=255, description="Имя исполнителя")
    department_id: int | None = Field(None, description="ID отдела (опционально)")
    user_id: int | None = Field(None, description="ID учётной записи (опционально, 1:1)")


class ExecutorUpdate(BaseModel):
    """Обновление исполнителя."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Новое имя")
    department_id: int | None = Field(None, description="Новый отдел (None = без отдела)")
    user_id: int | None = Field(None, description="Учётная запись (None = без привязки)")


class ExecutorResponse(BaseModel):
    """Ответ с данными исполнителя."""

    id: int
    name: str
    department_id: int | None
    department_name: str | None = None
    user_id: int | None = None
    user: ExecutorUserInfo | None = None

    model_config = ConfigDict(from_attributes=True)
