"""
Модель аудит-лога: фиксирует значимые события безопасности и действия с данными.
"""
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Запись аудита: кто, что, когда, откуда."""

    __tablename__ = "audit_log"

    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # Произвольная полезная нагрузка события (роли, счётчики и т.п.)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
