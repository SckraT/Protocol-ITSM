"""Утилиты времени."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Текущее время UTC без tzinfo (naive) — замена устаревшего datetime.utcnow().

    Возвращаем именно наивный UTC, а не aware-datetime:
    колонки created_at имеют тип TIMESTAMP WITHOUT TIME ZONE (asyncpg отвергает
    aware-datetime при вставке), а API отдаёт даты в ISO без смещения — формат ответа
    не должен измениться. Значение идентично прежнему datetime.utcnow().
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
