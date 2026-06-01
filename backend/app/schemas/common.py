"""
Общие схемы и перечисления, используемые в нескольких модулях.
"""
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class StateEnum(str, Enum):
    """Состояния задачи."""

    in_progress = "in_progress"
    postponed = "postponed"
    closed = "closed"


class PriorityEnum(str, Enum):
    """Приоритеты задачи."""

    high = "high"
    medium = "medium"
    low = "low"


class PaginatedResponse(BaseModel, Generic[T]):
    """Постраничный ответ с метаданными."""

    items: list[T]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке."""

    detail: str
