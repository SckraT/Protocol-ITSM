"""
Тестовый Prefect Flow для smoke-теста связки FastAPI ↔ Prefect.

Используется:
- POST /api/admin/test-flow — триггер из FastAPI для проверки работоспособности Prefect
- В Prefect UI видно выполненные flow runs (имя "hello-flow")

Реальные flow (SLA-эскалация, согласование Change) появятся в Этапах 2 и 4.
"""
from prefect import flow, task

from app.logging_config import logger


@task(
    name="greet-task",
    retries=3,
    retry_delay_seconds=[1, 5, 10],
    task_run_name="greet-{name}",
)
async def greet_task(name: str) -> str:
    """
    Атомарная задача: вернуть приветствие.
    retries=3, экспоненциальная задержка (1с, 5с, 10с) — по требованию НФТ.
    """
    logger.info("greet_task вызван с name=%s", name)
    return f"Hello, {name}!"


@flow(name="hello-flow", log_prints=True)
async def hello_flow(name: str = "world") -> str:
    """
    Тестовый flow: вызывает greet_task и возвращает результат.
    Доступен для прямого вызова (await hello_flow()) и через deployment.
    """
    result = await greet_task(name)
    print(f"Flow result: {result}")
    return result
