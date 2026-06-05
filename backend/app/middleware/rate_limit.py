"""
In-memory rate limiting (sliding window) для чувствительных эндпоинтов аутентификации.
Защищает от брутфорса. Рассчитан на один инстанс приложения; за балансировщиком
потребуется внешнее хранилище (Redis) — см. план улучшений.
"""
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Лимиты: путь → (макс. запросов, окно в секундах)
_LIMITS: dict[str, tuple[int, int]] = {
    "/api/auth/login": (5, 60),
    "/api/auth/refresh": (10, 60),
}

# Хранилище меток времени на уровне модуля: path → ip → метки.
# Модульный уровень упрощает сброс в тестах (reset_rate_limit).
_HITS: dict[str, dict[str, deque]] = defaultdict(lambda: defaultdict(deque))


def reset_rate_limit() -> None:
    """Очистить состояние лимитера (используется в тестах для изоляции)."""
    _HITS.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Ограничивает частоту запросов к auth-эндпоинтам по IP (sliding window)."""

    async def dispatch(self, request: Request, call_next):
        limit = _LIMITS.get(request.url.path)
        if limit is None:
            return await call_next(request)

        max_req, window = limit
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = _HITS[request.url.path][ip]

        # Убираем устаревшие метки за пределами окна
        while hits and now - hits[0] > window:
            hits.popleft()

        if len(hits) >= max_req:
            retry_after = int(window - (now - hits[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите позже."},
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        return await call_next(request)
