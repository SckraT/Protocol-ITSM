"""
Пакет Prefect workflows.

Содержит Flow и Task для долгоживущих и асинхронных бизнес-процессов:
- SLA-таймеры и эскалация инцидентов (Этап 2)
- Согласование Change Requests с таймаутом CAB (Этап 4)
- Служебные flow для smoke-теста связки FastAPI ↔ Prefect

Использование:
    from app.workflows.client import trigger_flow_run
    flow_run_id = await trigger_flow_run("sla-flow/check-sla", {"threshold_minutes": 15})
"""
