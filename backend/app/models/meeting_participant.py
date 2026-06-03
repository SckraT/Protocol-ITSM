"""
Ассоциативная таблица Many-to-Many: совещание ↔ участник (исполнитель).
Используется как Table-объект (без отдельного mapped class).
"""
from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base import Base

# Таблица связи совещания и участников (исполнителей)
meeting_participant_table = Table(
    "meeting_participants",
    Base.metadata,
    Column(
        "meeting_id",
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
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
