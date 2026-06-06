"""
Асинхронный клиент Redis (ленивая инициализация).

Используется rate-limiter'ом. Если REDIS_URL не задан — возвращает None,
и вызывающий код деградирует до in-memory (см. middleware/rate_limit.py).
"""
import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

_client: "aioredis.Redis | None" = None


def get_redis() -> "aioredis.Redis | None":
    """Вернуть общий Redis-клиент или None, если REDIS_URL не задан."""
    global _client
    if not settings.REDIS_URL:
        return None
    if _client is None:
        _client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    """Закрыть соединение с Redis (вызывается при остановке приложения)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
