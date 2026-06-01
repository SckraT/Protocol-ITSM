# Архитектура — Протокол совещаний v2.0

Документ описывает устройство приложения после переписывания на современный стек.

## Обзор

Приложение состоит из двух независимых частей:

- **`backend/`** — асинхронный API на FastAPI + SQLAlchemy 2.0 (aiosqlite).
- **`frontend/`** — SPA на Svelte 5 + SvelteKit (adapter-static) + Tailwind CSS.

В продакшене всё упаковывается в один Docker-образ: собранный фронтенд (`frontend/dist`)
кладётся в `static/` и раздаётся самим FastAPI. В dev-режиме фронтенд и бэкенд
работают раздельно (Vite на :5173, uvicorn на :8000).

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
SQLite (WAL) через async engine
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
| БД          | SQLite (WAL), aiosqlite, нормализованные M2M-связи                |
| Frontend    | Svelte 5, SvelteKit (adapter-static), Vite, Tailwind CSS, TypeScript |
| DevOps      | Docker (multi-stage), docker-compose (prod + dev)                 |
