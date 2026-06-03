"""
Протокол совещания v2.0 — точка входа FastAPI-приложения.

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
  - /health            — health check
  - /api/docs          — Swagger UI
"""
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine, get_db
from app.routers.auth import router as auth_router
from app.routers.departments import router as departments_router
from app.routers.executors import router as executors_router
from app.routers.export import import_router, router as export_router
from app.routers.items import router as items_router
from app.routers.meetings import router as meetings_router
from app.routers.statuses import router as statuses_router
from app.routers.users import router as users_router

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
    # Запуск миграций Alembic (создаёт/обновляет схему БД).
    # Используем модуль alembic.config (python -m alembic не работает — нет __main__).
    backend_dir = Path(__file__).parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "alembic.config", "upgrade", "head"],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Миграция не критична для запуска в dev-режиме (может быть уже применена)
        print(f"[alembic] {result.stderr}", flush=True)
    else:
        print("[alembic] Миграции применены успешно", flush=True)

    # Seed первого Admin (если таблица users пуста)
    await _seed_first_admin()

    yield

    # Закрываем соединения при остановке
    await engine.dispose()


async def _seed_first_admin() -> None:
    """
    Создать первого Admin, если пользователей ещё нет.
    Использует прямой async_session (не get_db), чтобы явно вызвать commit.
    get_db — генератор; break не вызывает код после yield, commit не выполняется.
    """
    from app.database import async_session as make_session
    from app.repositories.user_repository import UserRepository
    from app.services.auth_service import AuthService

    async with make_session() as session:
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
                print(f"[auth] Создан первый Admin: {user.username}", flush=True)
            else:
                print(f"[auth] Пользователи уже существуют ({count}), пропускаем seed", flush=True)
        except Exception as exc:
            await session.rollback()
            print(f"[auth] Ошибка при создании первого Admin: {exc}", flush=True)


# Инициализация FastAPI
app = FastAPI(
    title="Протокол совещания v2.0",
    description="API для управления задачами протокола совещания",
    version="2.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS — разрешаем фронтенд в dev-режиме
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры с префиксом /api
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(departments_router, prefix="/api")
app.include_router(executors_router, prefix="/api")
app.include_router(items_router, prefix="/api")
app.include_router(meetings_router, prefix="/api")
app.include_router(statuses_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(import_router, prefix="/api")


@app.get("/health", tags=["Система"], summary="Health check")
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "version": "2.2.0"}


# Раздача статики (собранный фронтенд) — только если директория существует
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
