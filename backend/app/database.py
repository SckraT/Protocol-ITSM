"""
Настройка подключения к базе данных.
Используется async SQLAlchemy 2.0 с aiosqlite для SQLite.
"""
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

# Получаем настройки
settings = get_settings()

# Убеждаемся, что директория для БД существует
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Async engine для SQLite с WAL-режимом
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={
        "check_same_thread": False,  # нужно для SQLite в многопоточной среде
        "timeout": 30,
    },
)

# Фабрика сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # объекты доступны после commit без reload
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI — предоставляет async-сессию БД.
    Автоматически выполняет commit при успехе и rollback при ошибке.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
