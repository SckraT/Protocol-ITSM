"""
Конфигурация приложения через pydantic-settings.
Значения загружаются из переменных окружения или .env файла.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # URL подключения к PostgreSQL (asyncpg-driver)
    DATABASE_URL: str = "postgresql+asyncpg://protocol:protocol@localhost:5432/protocol"

    # Режим отладки
    DEBUG: bool = False

    # Запускать миграции Alembic при старте приложения (в lifespan).
    # True (дефолт) — удобно для одноконтейнерного деплоя (текущее поведение).
    # False — если миграции применяются отдельным шагом (entrypoint/job/CI),
    # чтобы не запускать их в каждом web-воркере и не связывать старт с миграцией.
    RUN_MIGRATIONS_ON_STARTUP: bool = True

    # Разрешённые источники для CORS (через запятую)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8000"

    # JWT-аутентификация
    SECRET_KEY: str = "change-me-in-production-use-strong-random-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Первый Admin (создаётся автоматически при первом запуске)
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Возвращает список разрешённых origins для CORS."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Возвращает закешированный экземпляр настроек."""
    return Settings()
