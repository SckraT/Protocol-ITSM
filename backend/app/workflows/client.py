"""
Клиентские обёртки над Prefect API.

Единая точка вызова Prefect из services/ и routers/. Скрывает детали Prefect SDK,
добавляет таймауты, структурированное логирование и безопасный fallback.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger("protocol.workflows")


async def ping_prefect() -> bool:
    """
    Проверить доступность Prefect API по PREFECT_API_URL.
    Возвращает True если API ответил, False при любой ошибке.
    """
    settings = get_settings()
    try:
        from prefect.client.orchestration import get_client

        async with get_client() as client:
            # /health — лёгкий эндпоинт Prefect API
            response = await client._client.get("/health")
            ok = response.status_code == 200
            if ok:
                logger.info("Prefect API доступен: %s", settings.PREFECT_API_URL)
            else:
                logger.warning("Prefect API вернул %s: %s", response.status_code, settings.PREFECT_API_URL)
            return ok
    except Exception:
        logger.exception("Prefect API недоступен: %s", settings.PREFECT_API_URL)
        return False


async def trigger_flow_run(
    deployment_name: str,
    parameters: dict[str, Any] | None = None,
    timeout: float | None = None,
) -> str | None:
    """
    Запустить flow run через Prefect deployment (fire-and-forget).

    Возвращает flow_run_id (UUID) при успехе, None при ошибке.
    НЕ ждёт завершения flow — вызывающий код сразу получает управление.
    Используется из services/ для долгих операций (SLA-эскалация, согласование Change).

    Аргументы:
        deployment_name: имя deployment в формате "flow-name/deployment-name"
            (например, "sla-flow/check-sla-escalation").
        parameters: словарь параметров, передаваемых в flow.
        timeout: таймаут ожидания ответа Prefect API (по умолчанию PREFECT_TRIGGER_TIMEOUT из config).
    """
    settings = get_settings()
    if timeout is None:
        timeout = float(settings.PREFECT_TRIGGER_TIMEOUT)
    try:
        from prefect.deployments import run_deployment
    except ImportError:
        logger.error("Библиотека prefect не установлена — trigger_flow_run недоступен")
        return None

    try:
        flow_run = await asyncio.wait_for(
            run_deployment(
                name=deployment_name,
                parameters=parameters or {},
                timeout=timeout,
            ),
            timeout=timeout + 5,
        )
        flow_run_id = str(flow_run.id)
        logger.info(
            "Запущен flow run %s для deployment %s с параметрами %s",
            flow_run_id,
            deployment_name,
            parameters or {},
        )
        return flow_run_id
    except TimeoutError:
        logger.exception("Таймаут триггера deployment %s (%.1fс)", deployment_name, timeout)
        return None
    except Exception:
        logger.exception("Ошибка триггера deployment %s", deployment_name)
        return None


async def get_flow_run_state(flow_run_id: str) -> dict[str, Any] | None:
    """
    Получить текущее состояние flow run (для /api/changes/{id}/workflow-status).
    Возвращает словарь с name, type, message, или None при ошибке.
    """
    try:
        from prefect.client.orchestration import get_client

        async with get_client() as client:
            flow_run = await client.read_flow_run(flow_run_id)
            state = flow_run.state
            if state is None:
                return {"name": "Unknown", "type": "Unknown", "message": None}
            return {
                "name": state.name,
                "type": state.type,
                "message": state.message,
            }
    except Exception:
        logger.exception("Ошибка чтения flow run %s", flow_run_id)
        return None
