"""
Настройка логирования приложения.
Единый именованный логгер `protocol` с форматом «время уровень [имя] сообщение».
Пишем в stdout — в Docker это попадает в `docker logs`.
"""
import logging
import sys

# Корневой логгер приложения. Дочерние получаем через logging.getLogger("protocol.<area>").
logger = logging.getLogger("protocol")


def configure_logging(debug: bool = False) -> None:
    """Сконфигурировать логгер `protocol`. Идемпотентна (хендлер добавляется один раз)."""
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    # Не пробрасываем в root, чтобы не дублировать записи поверх хендлеров uvicorn.
    logger.propagate = False
