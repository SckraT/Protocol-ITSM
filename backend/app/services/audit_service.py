"""
Сервис аудита: запись значимых событий безопасности и действий с данными.
"""
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_event(
    session: AsyncSession,
    event_type: str,
    *,
    request: Request | None = None,
    username: str | None = None,
    payload: dict | None = None,
) -> None:
    """Записать событие в аудит-лог. IP/User-Agent берутся из request, если передан."""
    ip = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    session.add(
        AuditLog(
            event_type=event_type,
            username=username,
            ip=ip,
            user_agent=user_agent,
            payload=payload,
        )
    )
    await session.flush()
