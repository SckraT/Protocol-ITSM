"""
Пакет моделей SQLAlchemy.
Импортируем все модели чтобы Alembic видел их метаданные.
"""
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.department import Department
from app.models.executor import Executor
from app.models.item import Item
from app.models.item_executor import item_executor_table
from app.models.meeting import Meeting
from app.models.meeting_participant import meeting_participant_table
from app.models.status import Status
from app.models.user import User

__all__ = [
    "AuditLog",
    "Base",
    "Department",
    "Executor",
    "Item",
    "item_executor_table",
    "Meeting",
    "meeting_participant_table",
    "Status",
    "User",
]
