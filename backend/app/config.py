"""
Конфигурация приложения через pydantic-settings.
Значения загружаются из переменных окружения или .env файла.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Путь к базе данных SQLite
    DB_PATH: str = str(Path(__file__).parent.parent.parent / "data" / "protocol.db")

    # Режим отладки
    DEBUG: bool = False

    # Разрешённые источники для CORS (через запятую)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL для SQLAlchemy async driver."""
        return f"sqlite+aiosqlite:///{self.DB_PATH}"

    @property
    def cors_origins(self) -> list[str]:
        """Возвращает список разрешённых origins для CORS."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Возвращает закешированный экземпляр настроек."""
    return Settings()
