"""
Админ-эндпоинты для Prefect: smoke-тест связки FastAPI ↔ Prefect.

Доступ: только Admin (require_admin).

POST /api/admin/test-flow
    1. Пингует Prefect API (PREFECT_API_URL).
    2. Если есть deployment hello-flow/hello-flow — триггерит через run_deployment (fire-and-forget).
    3. Иначе — прямой вызов hello_flow() (для smoke-теста без настроенного deployment).
    4. Возвращает 202 Accepted + статус/flow_run_id.

Используется для проверки Этапа 1 (инфраструктура Prefect).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import require_admin
from app.models.user import User
from app.workflows.client import ping_prefect, trigger_flow_run
from app.workflows.hello_flow import hello_flow

router = APIRouter(prefix="/admin", tags=["Администрирование (служебные)"])


@router.post(
    "/test-flow",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Smoke-тест Prefect: триггер hello-flow",
)
async def trigger_test_flow(
    _admin: User = Depends(require_admin),
) -> dict[str, str]:
    """
    Запустить тестовый flow для проверки связки с Prefect.
    Возвращает 202 + flow_run_id (или результат при прямом вызове).
    """
    prefect_ok = await ping_prefect()
    if not prefect_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prefect API недоступен. Проверьте, что prefect-server healthy.",
        )

    # Пробуем через deployment (production-паттерн)
    flow_run_id = await trigger_flow_run(
        deployment_name="hello-flow/hello-flow",
        parameters={"name": "smoke-test"},
        timeout=5,
    )
    if flow_run_id is not None:
        return {
            "status": "triggered",
            "mode": "deployment",
            "flow_run_id": flow_run_id,
        }

    # Fallback: прямой вызов flow (для smoke-теста без настроенного deployment)
    try:
        result = await hello_flow(name="smoke-test")
        return {
            "status": "ok",
            "mode": "direct",
            "result": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка выполнения flow: {exc}",
        )
