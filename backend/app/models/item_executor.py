"""
Ассоциативная таблица Many-to-Many: задача ↔ исполнитель.
Используется как Table-объект (без отдельного mapped class),
т.к. не содержит дополнительных полей.
"""
from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base import Base

# Таблица связи задачи и исполнителей
item_executor_table = Table(
    "item_executors",
    Base.metadata,
    Column(
        "item_id",
        Integer,
        ForeignKey("items.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "executor_id",
        Integer,
        ForeignKey("executors.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)
