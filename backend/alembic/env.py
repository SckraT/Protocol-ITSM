"""
Конфигурация среды Alembic — async-режим для SQLAlchemy 2.0 с asyncpg.
URL базы данных берётся из Settings, а не из alembic.ini.
"""
import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Добавляем backend/ в путь для импорта app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.models import Base  # noqa: E402 — импорт после sys.path

# Объект конфигурации Alembic
config = context.config

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные всех моделей для автогенерации миграций
target_metadata = Base.metadata


def get_url() -> str:
    """Возвращает URL БД из настроек приложения."""
    settings = get_settings()
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме (без подключения к БД).
    Используется для генерации SQL-скриптов.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняет миграции с активным соединением."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запуск миграций в async-режиме через asyncpg."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме (async)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
