"""
Protocol-ITSM — точка входа FastAPI-приложения.

Структура:
  - /api/auth          — аутентификация (login, refresh, me)
  - /api/users         — управление пользователями (только Admin)
  - /api/departments   — справочник отделов
  - /api/executors     — справочник исполнителей
  - /api/items         — задачи протокола
  - /api/items/{id}/statuses — история статусов
  - /api/statuses/{id} — удаление записи статуса
  - /api/export/csv    — экспорт CSV
  - /api/export/xlsx   — экспорт Excel
  - /api/import/csv    — импорт CSV
  - /api/admin/test-flow — smoke-тест Prefect (только Admin)
  - /health            — health check
  - /health/detailed   — расширенный health check (БД + alembic)
  - /api/docs          — Swagger UI
"""
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database import async_session, engine
from app.dependencies import forbid_pending_password_change
from app.logging_config import configure_logging, logger
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis_client import close_redis
from app.repositories.user_repository import UserRepository
from app.routers.auth import router as auth_router
from app.routers.departments import router as departments_router
from app.routers.executors import router as executors_router
from app.routers.export import import_router
from app.routers.export import router as export_router
from app.routers.items import router as items_router
from app.routers.meetings import router as meetings_router
from app.routers.statuses import router as statuses_router
from app.routers.users import router as users_router
from app.routers.workflows import router as workflows_router
from app.services.auth_service import AuthService

settings = get_settings()

# Путь к директории со статикой (собранный фронтенд)
STATIC_DIR = Path(__file__).parent.parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Жизненный цикл приложения:
    - При старте: запускаем миграции Alembic.
    - При остановке: закрываем engine.
    """
    # Настраиваем логирование как можно раньше в жизненном цикле.
    configure_logging(debug=settings.DEBUG)

    # Запуск миграций Alembic (создаёт/обновляет схему БД). Можно отключить через
    # RUN_MIGRATIONS_ON_STARTUP=False, если миграции применяются отдельным шагом.
    if settings.RUN_MIGRATIONS_ON_STARTUP:
        # Используем модуль alembic.config (python -m alembic не работает — нет __main__).
        backend_dir = Path(__file__).parent.parent
        result = subprocess.run(
            [sys.executable, "-m", "alembic.config", "upgrade", "head"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Реальный сбой миграции нельзя глотать: иначе приложение поднимется
            # на неполной схеме и будет отдавать 500 на запросах. Прерываем старт.
            logger.error("[alembic] ОШИБКА применения миграций:\n%s", result.stderr)
            raise RuntimeError("Не удалось применить миграции Alembic — запуск прерван")
        logger.info("[alembic] Миграции применены успешно")
    else:
        logger.info("[alembic] Пропуск миграций при старте (RUN_MIGRATIONS_ON_STARTUP=False)")

    # Проверка небезопасных дефолтов. В проде дефолтный SECRET_KEY фатален
    # (ключ публичен в репозитории — атакующий подпишет любой admin-JWT).
    _default_secret = "change-me-in-production-use-strong-random-key"
    if settings.SECRET_KEY == _default_secret:
        if not settings.DEBUG:
            raise RuntimeError(
                "Дефолтный SECRET_KEY недопустим в продакшне. "
                "Задайте SECRET_KEY в .env (openssl rand -hex 32)."
            )
        logger.warning("[security] ВНИМАНИЕ: дефолтный SECRET_KEY (только для dev)!")

    # Дефолтный пароль администратора — громкое предупреждение (действует только
    # при пустой таблице users, поэтому не фатально).
    if settings.FIRST_ADMIN_PASSWORD == "admin":
        logger.warning(
            "[security] ВНИМАНИЕ: используется дефолтный пароль администратора 'admin'! "
            "Смените FIRST_ADMIN_PASSWORD в .env до первого запуска."
        )

    # CORS: в проде ALLOWED_ORIGINS должен указывать боевой домен, не localhost.
    # В дев-режиме localhost ожидаем — не предупреждаем.
    if not settings.DEBUG and "localhost" in settings.ALLOWED_ORIGINS:
        logger.warning(
            "[security] ВНИМАНИЕ: ALLOWED_ORIGINS содержит 'localhost' в не-DEBUG режиме! "
            "Задайте боевой домен в .env (например, https://protocol.example.com)."
        )

    # Seed первого Admin (если таблица users пуста)
    await _seed_first_admin()

    yield

    # Закрываем соединения при остановке
    await engine.dispose()
    await close_redis()


async def _seed_first_admin() -> None:
    """
    Создать первого Admin, если пользователей ещё нет.
    Использует прямой async_session (не get_db), чтобы явно вызвать commit.
    get_db — генератор; break не вызывает код после yield, commit не выполняется.
    """
    async with async_session() as session:
        try:
            repo = UserRepository(session)
            count = await repo.count_all()
            if count == 0:
                service = AuthService(session)
                user = await service.create_first_admin(
                    username=settings.FIRST_ADMIN_USERNAME,
                    password=settings.FIRST_ADMIN_PASSWORD,
                )
                await session.commit()
                logger.info("[auth] Создан первый Admin: %s", user.username)
            else:
                logger.info("[auth] Пользователи уже существуют (%d), пропускаем seed", count)
        except Exception:
            await session.rollback()
            logger.exception("[auth] Ошибка при создании первого Admin")


# Инициализация FastAPI
app = FastAPI(
    title="Protocol-ITSM",
    description="API ITSM-платформы (Инциденты, Проблемы, Изменения) на базе Протокола совещаний",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — разрешаем фронтенд. Origins из настроек; методы/заголовки сужены до фактически
# используемых (не wildcard) — принцип наименьших привилегий.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Rate limiting на auth-эндпоинты (защита от брутфорса)
app.add_middleware(RateLimitMiddleware)

# Базовый guard «требуется авторизация» на уровне роутера — чтобы новый эндпоинт
# по умолчанию был закрыт, а не открыт (мутации дополнительно требуют require_editor).
# Также блокирует доступ, пока не сменён обязательный пароль (forbid_pending_password_change).
_auth = [Depends(forbid_pending_password_change)]

# /auth — открыт (login/refresh); /users — уже под require_admin на уровне роутера.
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(departments_router, prefix="/api", dependencies=_auth)
app.include_router(executors_router, prefix="/api", dependencies=_auth)
app.include_router(items_router, prefix="/api", dependencies=_auth)
app.include_router(meetings_router, prefix="/api", dependencies=_auth)
app.include_router(statuses_router, prefix="/api", dependencies=_auth)
app.include_router(export_router, prefix="/api", dependencies=_auth)
app.include_router(import_router, prefix="/api", dependencies=_auth)
# /admin/* — собственная авторизация (require_admin на каждом эндпоинте роутера)
app.include_router(workflows_router, prefix="/api")


@app.get("/health", tags=["Система"], summary="Health check")
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "version": "3.0.0"}


@app.get("/health/detailed", tags=["Система"], summary="Расширенный health check")
async def health_detailed():
    """Проверка соединения с БД и текущей версии миграции Alembic."""
    db_ok = False
    alembic_version: str | None = None
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            row = result.first()
            alembic_version = row[0] if row else None
    except Exception:
        db_ok = False

    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status": "ok" if db_ok else "degraded",
            "version": app.version,
            "database": "ok" if db_ok else "unavailable",
            "alembic_version": alembic_version,
        },
    )


# Раздача статики (собранный фронтенд SPA) — только если директория существует.
# SvelteKit (adapter-static) делает клиентский роутинг: на любой неизвестный путь
# нужно отдавать index.html, иначе перезагрузка страницы вроде /meetings даёт 404.
if STATIC_DIR.exists():
    _index_html = STATIC_DIR / "index.html"

    # Хешированные ассеты сборки — отдаём через StaticFiles (корректные заголовки/кеш)
    app.mount("/_app", StaticFiles(directory=str(STATIC_DIR / "_app")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Отдать конкретный файл, если он есть, иначе — entry SPA (клиентский роутинг)."""
        # Неизвестные /api — это реальный 404 API, а не страница SPA
        if full_path == "api" or full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Конкретный существующий файл (favicon.ico и т.п.) — с защитой от обхода пути
        if full_path:
            candidate = (STATIC_DIR / full_path).resolve()
            if candidate.is_file() and str(candidate).startswith(str(STATIC_DIR.resolve())):
                return FileResponse(candidate)

        # Иначе — index.html, дальше роутинг на клиенте
        return FileResponse(_index_html)
