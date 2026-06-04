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

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine, get_db
from app.dependencies import get_current_user
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
        # Реальный сбой миграции нельзя глотать: иначе приложение поднимется
        # на неполной схеме и будет отдавать 500 на запросах. Прерываем старт.
        print(f"[alembic] ОШИБКА применения миграций:\n{result.stderr}", flush=True)
        raise RuntimeError("Не удалось применить миграции Alembic — запуск прерван")
    print("[alembic] Миграции применены успешно", flush=True)

    # Проверка небезопасных дефолтов. В проде дефолтный SECRET_KEY фатален
    # (ключ публичен в репозитории — атакующий подпишет любой admin-JWT).
    _default_secret = "change-me-in-production-use-strong-random-key"
    if settings.SECRET_KEY == _default_secret:
        if not settings.DEBUG:
            raise RuntimeError(
                "Дефолтный SECRET_KEY недопустим в продакшне. "
                "Задайте SECRET_KEY в .env (openssl rand -hex 32)."
            )
        print("[security] ВНИМАНИЕ: дефолтный SECRET_KEY (только для dev)!", flush=True)

    # Дефолтный пароль администратора — громкое предупреждение (действует только
    # при пустой таблице users, поэтому не фатально).
    if settings.FIRST_ADMIN_PASSWORD == "admin":
        print(
            "[security] ВНИМАНИЕ: используется дефолтный пароль администратора 'admin'! "
            "Смените FIRST_ADMIN_PASSWORD в .env до первого запуска.",
            flush=True,
        )

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
    version="2.4.0",
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

# Базовый guard «требуется авторизация» на уровне роутера — чтобы новый эндпоинт
# по умолчанию был закрыт, а не открыт (мутации дополнительно требуют require_editor).
_auth = [Depends(get_current_user)]

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


@app.get("/health", tags=["Система"], summary="Health check")
async def health_check():
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "version": "2.4.0"}


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
