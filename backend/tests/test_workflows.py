"""
Тесты для Prefect workflows.

Проверяем, что hello_flow и greet_task можно вызвать как обычные async-функции
(без поднятого Prefect-сервера). Prefect-декораторы (@flow, @task) сохраняют
вызываемость функций, но добавляют обвязку для оркестратора.
"""
import pytest

from app.workflows.hello_flow import greet_task, hello_flow


@pytest.mark.asyncio
async def test_greet_task_returns_greeting():
    """greet_task возвращает строку приветствия."""
    result = await greet_task("alice")
    assert result == "Hello, alice!"


@pytest.mark.asyncio
async def test_hello_flow_returns_greeting():
    """hello_flow выполняет greet_task и возвращает результат."""
    result = await hello_flow(name="bob")
    assert result == "Hello, bob!"


@pytest.mark.asyncio
async def test_hello_flow_default_name():
    """hello_flow использует имя 'world' по умолчанию."""
    result = await hello_flow()
    assert result == "Hello, world!"


def test_greet_task_has_retries_configured():
    """greet_task должен иметь retries=3 по НФТ (надёжность)."""
    # Prefect-декоратор @task сохраняет retries в атрибутах объекта.
    # Проверяем, что retries настроены (>= 1) — иначе нарушается НФТ.
    assert greet_task.retries is not None
    assert greet_task.retries >= 1


def test_hello_flow_has_name():
    """hello_flow должен иметь имя для отображения в Prefect UI."""
    assert hello_flow.name == "hello-flow"
