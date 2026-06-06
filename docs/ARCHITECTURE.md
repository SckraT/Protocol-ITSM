# Архитектура — Protocol-ITSM v3.0.0

Документ описывает устройство приложения. Начиная с v3.0.0 репозиторий продолжается
как `SckraT/Protocol-ITSM` (форк `SckraT/Meeting-Minutes` v2.7.0): к слоистой
архитектуре добавлен пакет `app/workflows/` и три новых docker-сервиса для Prefect.

## Обзор

Приложение состоит из трёх групп сервисов:

- **`backend/` + `frontend/`** — без изменений от v2.0: FastAPI API + Svelte 5 SPA
  (см. исторические разделы ниже).
- **Prefect 3** — оркестратор flow (SLA-эскалация, согласование Change, rollback).
  Три контейнера: `prefect-db` (PostgreSQL для состояния Prefect), `prefect-server`
  (API + UI на `:4200`), `prefect-worker` (исполнитель flow в work pool `default`).

В продакшене всё упаковывается в один Docker-образ: собранный фронтенд (`frontend/dist`)
кладётся в `static/` и раздаётся самим FastAPI. Prefect-сервисы идут отдельными
контейнерами. В dev-режиме бэкенд/фронтенд/Prefect поднимаются через
`docker-compose.dev.yml` (hot-reload на бэкенде, UI Prefect на :4200).

## Backend: слоистая архитектура

```
HTTP-запрос
   │
   ▼
routers/        — HTTP-слой: валидация, коды ответов, DI сессии (Depends(get_db))
   │
   ▼
services/       — бизнес-логика: сериализация, агрегаты, координация репозиториев
   │
   ▼
repositories/   — доступ к данным: запросы SQLAlchemy, BaseRepository[T]
   │
   ▼
models/         — ORM-модели (Mapped[T], mapped_column), связи, каскады
   │
   ▼
PostgreSQL 16 через async engine
```

### Ключевые принципы

- **Управление транзакцией централизовано.** Репозитории вызывают `flush()`, а не
  `commit()`. Коммит/откат выполняет зависимость `get_db()` в `database.py`:
  успешный запрос → commit, исключение → rollback.
- **Lazy loading запрещён в async.** Все связи грузятся явно через `selectinload(...)`
  (иначе SQLAlchemy бросает `MissingGreenlet`). См. `item_repository.py`:
  `selectinload(Item.executors).selectinload(Executor.department)` + `selectinload(Item.statuses)`.
- **Generic-репозиторий.** `BaseRepository[T]` даёт типобезопасный CRUD; конкретные
  репозитории добавляют специфичные запросы (фильтры, выборка последних статусов).
- **Pydantic v2 на границе.** Схемы (`schemas/`) отделены от ORM-моделей.
  В Create/Update используется `executor_ids: list[int]`, в Response — `executors: list[ExecutorInItem]`.

### Модель данных

| Таблица           | Назначение                                   |
| ----------------- | -------------------------------------------- |
| `departments`     | Справочник отделов                           |
| `executors`       | Исполнители (FK → departments, `SET NULL`)   |
| `items`           | Задачи протокола                             |
| `statuses`        | История статусов (FK → items, `CASCADE`)     |
| `item_executors`  | **M2M** связь задач и исполнителей           |

Главное отличие от v1 — нормализация: вместо колонки `executors_json` (JSON-массив
ID) введена ассоциативная таблица `item_executors`. Это позволяет фильтровать и
джойнить по исполнителям средствами SQL.

### Миграции

Alembic в async-режиме. `alembic.ini` не содержит `sqlalchemy.url` — URL берётся в
`env.py` из `Settings` (`config.py`). Миграции применяются автоматически при старте
приложения (lifespan в `main.py`) и в Docker CMD (`alembic upgrade head`).

## Frontend: Svelte 5 + SvelteKit

```
routes/                 — страницы (SPA): +layout, +page (задачи), refs/+page
   │
   ├─ components/
   │    ui/             — переиспользуемые примитивы (Button, Drawer, Modal, …)
   │    items/          — таблица, строка, drawer, формы, timeline, bulk
   │    refs/           — справочники (отделы, исполнители)
   │    common/         — Dashboard, SearchBar, Pagination, ConfirmDialog
   │
   ├─ stores/ (*.svelte.ts) — состояние на Svelte 5 Runes
   │    items, filters, selection, theme, refs, toast, confirm
   │
   ├─ api/              — HTTP-клиент и модули по сущностям
   └─ utils/            — даты, форматирование, константы
```

### Ключевые принципы

- **Runes вместо сторов Svelte 4.** Состояние — `$state`, производные значения —
  `$derived`/`$derived.by`. Файлы сторов имеют расширение `.svelte.ts` (обязательно,
  иначе руны не компилируются).
- **Оптимистичный UI.** `itemsStore.update/remove` применяют изменение немедленно,
  сохраняя снимок; при ошибке API — откат и toast.
- **Безопасность.** Никаких inline-обработчиков и конкатенации HTML — Svelte
  экранирует вывод автоматически (устранение XSS из v1).
- **Тема.** Атрибут `data-theme` на `<html>`; предзагрузка в `app.html` против FOUC;
  fallback на `prefers-color-scheme`.
- **SPA-режим.** `adapter-static` с `fallback: index.html`, `ssr = false`.
  Сборка кладётся в `dist/`, который копируется в `static/` образа.

### Сквозная типизация

Типы фронтенда (`lib/api/types.ts`) соответствуют Pydantic-схемам. При запущенном
бэкенде их можно перегенерировать из OpenAPI: `npm run generate-types`.

## Технологический стек

| Слой        | Технологии                                                        |
| ----------- | ----------------------------------------------------------------- |
| Backend     | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| БД          | PostgreSQL 16 (asyncpg), нормализованные M2M-связи                 |
| Frontend    | Svelte 5, SvelteKit (adapter-static), Vite, Tailwind CSS, TypeScript |
| Оркестрация | Prefect 3 (`app/workflows/` + 3 docker-сервиса: db, server, worker) |
| DevOps      | Docker (multi-stage), docker-compose (prod + dev + local-prod)     |

## Оркестрация (Prefect) — Этап 1

### Зачем

Некоторые бизнес-процессы нельзя выполнять синхронно в HTTP-запросе:

- **SLA-эскалация** — по расписанию каждую минуту: проверить инциденты с истекающим
  дедлайном, повысить приоритет, перевести на следующий уровень поддержки.
- **Согласование Change (CAB)** — ждать до 72ч, пока approver одобрит/отклонит.
  Нельзя держать HTTP-сокет открытым три дня.
- **Компенсирующие операции (rollback)** — при падении Change запустить Task
  «откатить изменения», создать incident.

Prefect решает это: гарантированно выполняет async-задачи, ретраит при сбоях (до 3
попыток по НФТ), показывает в UI (`:4200`) историю, логи, состояние.

### Поток данных

```
HTTP-запрос → FastAPI router → service → trigger_flow_run()
    │                                            │
    │                                            ▼
    │                              Prefect API (prefect-server)
    │                                            │
    │            ┌───────────────────────────────┘
    │            ▼
    │     Prefect DB (prefect-db) — состояние flow run, deployments
    │
    │   ← 202 Accepted + flow_run_id (неблокирующий ответ)
    │
    └── Асинхронно: worker забирает задачу, выполняет @task'и,
        обновляет состояние в prefect-db. UI на :4200 показывает прогресс.
```

### Где живёт код

- `app/workflows/` — Flow и Task. Каждый flow — `@flow(name=..., log_prints=True)`,
  задачи — `@task(retries=3, retry_delay_seconds=[1, 5, 10])`.
- `app/workflows/client.py` — клиентские обёртки:
  - `ping_prefect()` — проверка доступности API.
  - `trigger_flow_run(deployment_name, parameters, timeout)` —
    fire-and-forget через `prefect.deployments.run_deployment`. Возвращает
    `flow_run_id` или `None` (при таймауте/ошибке).
  - `get_flow_run_state(flow_run_id)` — для `GET /api/changes/{id}/workflow-status`.
- `app/routers/workflows.py` — `POST /api/admin/test-flow` (require_admin) — smoke-тест.

### Конвенция вызова из services/

Любой `service/`, инициирующий долгий процесс, **возвращает `202 Accepted`** +
`{"flow_run_id": "..."}`. Это требование масштабируется: SLA-эскалация в Этапе 2,
согласование Change в Этапе 4. Пример шаблона:

```python
flow_run_id = await trigger_flow_run(
    "sla-flow/check-sla-escalation",
    parameters={"threshold_minutes": 15},
)
# flow_run_id может быть None — тогда логируем и продолжаем без Prefect
```

### Аутентификация Prefect

`PREFECT_SERVER_API_AUTH_STRING` (basic auth). Должен быть **одинаковый** на
`prefect-server` и на всех клиентах (`prefect-worker`, `protocol`). В dev — пусто.
В проде — в `.env` (см. `.env.example`).

### Smoke-тест Этапа 1

`POST /api/admin/test-flow` (admin token) → пингует Prefect API → если есть
deployment `hello-flow/hello-flow`, триггерит его; иначе вызывает `hello_flow()`
напрямую. Возвращает `202 + flow_run_id` или `result` (при прямом вызове). На
:4200 (UI) виден flow run с именем `hello-flow`.
