"""
Rate limiting (sliding window) для чувствительных эндпоинтов аутентификации.
Защищает от брутфорса.

Бэкенд:
  - Redis (если задан REDIS_URL) — общий для всех воркеров/инстансов, переживает рестарт.
  - In-memory fallback — один инстанс; для dev/тестов и при недоступности Redis.

IP клиента определяется с учётом reverse-proxy (X-Real-IP / X-Forwarded-For):
без этого за nginx все клиенты выглядели бы как один IP (IP прокси), и лимит
блокировал бы вход всем сразу, не различая атакующих.
"""
import time
import uuid
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import logger
from app.redis_client import get_redis

# Лимиты: путь → (макс. запросов, окно в секундах)
_LIMITS: dict[str, tuple[int, int]] = {
    "/api/auth/login": (5, 60),
    "/api/auth/refresh": (10, 60),
}

# In-memory fallback: path → ip → метки времени (monotonic).
# Модульный уровень упрощает сброс в тестах (reset_rate_limit).
_HITS: dict[str, dict[str, deque]] = defaultdict(lambda: defaultdict(deque))


def reset_rate_limit() -> None:
    """Очистить in-memory состояние лимитера (используется в тестах для изоляции)."""
    _HITS.clear()


def _client_ip(request: Request) -> str:
    """
    Реальный IP клиента с учётом reverse-proxy.
    nginx проставляет X-Real-IP (= remote_addr) и X-Forwarded-For. Backend наружу
    не публикуется (только через nginx), поэтому заголовкам можно доверять; при
    прямом подключении (dev/тесты) их нет — берём request.client.host.
    """
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # Левый адрес — исходный клиент (далее идут прокси)
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_memory(path: str, ip: str, max_req: int, window: int) -> tuple[bool, int]:
    """In-memory sliding window. Возвращает (allowed, retry_after)."""
    now = time.monotonic()
    hits = _HITS[path][ip]
    # Убираем устаревшие метки за пределами окна
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= max_req:
        retry_after = int(window - (now - hits[0])) + 1
        return False, retry_after
    hits.append(now)
    return True, 0


async def _check_redis(client, path: str, ip: str, max_req: int, window: int) -> tuple[bool, int]:
    """
    Sliding window через Redis ZSET (score = unix-время, member уникален).
    Атомарно: удаляем устаревшие, добавляем текущий, считаем, ставим TTL.
    """
    key = f"rl:{path}:{ip}"
    now = time.time()
    member = f"{now}:{uuid.uuid4().hex}"
    async with client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {member: now})
        pipe.zcard(key)
        pipe.expire(key, window)
        _, _, count, _ = await pipe.execute()

    if count > max_req:
        # Время самого старого запроса в окне → остаток до разблокировки
        oldest = await client.zrange(key, 0, 0, withscores=True)
        retry_after = window
        if oldest:
            retry_after = int(window - (now - oldest[0][1])) + 1
        return False, max(retry_after, 1)
    return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Ограничивает частоту запросов к auth-эндпоинтам по IP (sliding window)."""

    async def dispatch(self, request: Request, call_next):
        limit = _LIMITS.get(request.url.path)
        if limit is None:
            return await call_next(request)

        max_req, window = limit
        ip = _client_ip(request)
        path = request.url.path

        client = get_redis()
        if client is not None:
            try:
                allowed, retry_after = await _check_redis(client, path, ip, max_req, window)
            except Exception:
                # Redis недоступен — деградируем до in-memory (per-instance), не роняем auth
                logger.warning("[rate-limit] Redis недоступен, fallback на in-memory")
                allowed, retry_after = _check_memory(path, ip, max_req, window)
        else:
            allowed, retry_after = _check_memory(path, ip, max_req, window)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите позже."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
