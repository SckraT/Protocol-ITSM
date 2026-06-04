"""
Настройка подключения к базе данных.
Используется async SQLAlchemy 2.0 с asyncpg для PostgreSQL.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

# Получаем настройки
settings = get_settings()

# Async engine для PostgreSQL с connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
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
