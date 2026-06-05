# Техническое задание: улучшение качества проекта «Протокол совещаний»

**Версия:** 2.6.8 | **Бэкенд:** `backend/app/` | **Тесты:** `backend/tests/`

---

## Блок 1: CI/CD (GitHub Actions) — КРИТИЧНО

**Проблема:** `.github/` не существует. Нулевая автоматизация — все проверки вручную.

**Задача:** Создать `.github/workflows/ci.yml`

**Требования к пайплайну:**

| Шаг | Команда | Условие |
|-----|---------|---------|
| Линт бэкенда | `ruff check backend/app/` | На push в `beta` и `main`, а также PR |
| Тесты бэкенда | `cd backend && pytest tests/ -v --cov=app --cov-report=term-missing` | То же |
| Типизация бэкенда (опц.) | `cd backend && pyright app/ \|\| true` или mypy | То же |
| Сборка Docker | `docker compose -f docker-compose.prod.yml build` | Только PR → main |
| Фронтенд-проверка (опц.) | `cd frontend && npm run check` (svelte-check) | На push в `beta`/`main` |

**Окружение:** `ubuntu-latest`, Python 3.12+, Node.js 20

**Кэширование:** `~/.cache/pip`, `node_modules` для ускорения

**Артефакты:** Отчёт о покрытии загрузить как artifact при падении

**Файл:** `.github/workflows/ci.yml` (новый)

---

## Блок 2: Тестирование — ВЫСОКИЙ ПРИОРИТЕТ

### 2.1. Добавить pytest-cov в зависимости

**Файл:** `backend/pyproject.toml`, секция `dev`
```toml
dev = [
    ...,
    "pytest-cov>=5.0.0",   # добавить
]
```

Добавить в `[tool.pytest.ini_options]`:
```toml
addopts = "--cov=app --cov-report=term-missing"
```

### 2.2. Новые тестовые файлы (следовать паттерну из `test_items_api.py` / `test_departments_api.py`)

**Паттерн существующих тестов:**
- `@pytest.mark.asyncio` декоратор
- Фикстуры: `client` (admin), `editor_client`, `viewer_client`, `anon_client`
- HTTP-запросы через `httpx.AsyncClient` с ASGI-транспортом
- Русские docstring'и на каждом тесте
- Проверки `status_code` + структуры JSON-ответа

#### Файл 1: `tests/test_meetings_api.py` (~8-10 тестов)

Цель: покрыть `backend/app/routers/meetings.py` (5 эндпоинтов)

| Тест | Что проверяем | Ожидаемый результат |
|------|--------------|---------------------|
| `test_list_meetings_empty` | GET `/api/meetings` при пустой БД | 200, `items == []` |
| `test_create_meeting` | POST `/api/meetings` с `{title, meeting_date}` | 201, вернулся созданный объект |
| `test_create_meeting_with_participants` | POST + `participant_ids` (сначала создать исполнителя) | 201, `participants` заполнен |
| `test_get_meeting` | GET `/api/meetings/{id}` после create | 200, правильный id |
| `test_get_meeting_not_found` | GET `/api/meetings/999` | 404 |
| `test_update_meeting` | PATCH заголовок | 200, новый title в ответе |
| `test_delete_meeting` | DELETE → GET того же id | 204 → 404 |
| `test_meetings_require_auth` | GET без токена (`anon_client`) | 401 |
| `test_editor_can_create` | POST от `editor_client` | 201 |
| `test_viewer_cannot_create` | POST от `viewer_client` | 403 |

**Схемы для референса:** `MeetingCreate` (`schemas/meeting.py`) — поля: `title` (str ≥1), `meeting_date` (date|null), `description` (str|null), `participant_ids` (list[int])

#### Файл 2: `tests/test_executors_api.py` (~7-8 тестов)

Цель: покрыть `backend/app/routers/executors.py` (5 эндпоинтов)

| Тест | Что проверяем | Ожидаемый результат |
|------|--------------|---------------------|
| `test_list_executors_empty` | GET `/api/executors` | 200, `[]` |
| `test_create_executor` | POST `/api/executors` `{name}` | 201 |
| `test_create_executor_duplicate` | POST с тем же name | 409 |
| `test_create_executor_with_department` | POST + предварительно созданный department | 201, `department_name` заполнен |
| `test_update_executor` | PUT имя + другой department | 200 |
| `test_delete_executor` | DELETE → GET | 204 → 404 |
| `test_user_options` | GET `/api/executors/user-options` от editor | 200, список с `id`+`username` |
| `test_user_options_viewer_forbidden` | GET от viewer | 403 |

**Схемы:** `ExecutorCreate` (`schemas/executor.py`) — `name` (str≥1, max255), `department_id` (int|null), `user_id` (int|null)

#### Файл 3: `tests/test_users_api.py` (~8-10 тестов)

Цель: покрыть `backend/app/routers/users.py` (4 эндпоинта). **Все требуют admin-роли.**

| Тест | Что проверяем | Ожидаемый результат |
|------|--------------|---------------------|
| `test_list_users_admin` | GET `/api/users` от admin | 200, список |
| `test_list_users_editor_forbidden` | GET от editor | 403 |
| `test_create_user` | POST `/api/users` {username, password, role, last_name, first_name} | 201 |
| `test_create_user_duplicate_username` | POST с существующим username | 409 |
| `test_update_user_role` | PATCH роль на viewer→editor | 200, новая роль |
| `test_update_self_role_forbidden` | PATCH свой own user_id → сменить роль | 400 ("Нельзя изменить роль...") |
| `test_deactivate_self_forbidden` | PATCH свой `is_active=False` | 400 |
| `test_delete_user` | DELETE созданного пользователя | 204 |
| `test_delete_self_forbidden` | DELETE свой user_id | 400 ("Нельзя удалить собственный аккаунт") |

**Важно:** Для тестов self-protection нужен отдельный admin-клиент с известным id (создать второго admin через `_seed_user`). См. `users.py:81-88,139-143`.

**Схемы:** `UserCreate` (`schemas/user.py`) — `username`(str≥3), `password`(str≥8), `role`(enum), `last_name`, `first_name`(обяз), `email`(EmailStr|null), `phone`(str|null)

#### Файл 4: `tests/test_statuses_api.py` (~5-6 тестов)

Цель: покрыть `backend/app/routers/statuses.py` (3 эндпоинта)

| Тест | Что проверяем | Ожидаемый результат |
|------|--------------|---------------------|
| `test_list_statuses_empty` | GET `/api/items/{item_id}/statuses` | 200, `[]` |
| `test_add_status` | POST статус к созданной item | 201, `status_note` совпадает |
| `test_delete_status` | DELETE созданного статуса | 204 |
| `test_status_item_not_found` | GET `/api/items/999/statuses` | 404 |
| `test_add_status_viewer_forbidden` | POST от viewer | 403 |
| `test_multiple_statuses_chronological` | Добавить 3 статуса, проверить порядок | 200, reverse chronological |

**Схемы:** `StatusCreate` (`schemas/status.py`) — `status_date`(date|null), `status_note`(str|null)

### 2.3. Расширить conftest.py

**Файл:** `backend/tests/conftest.py`

Добавить хелперы для создания связанных сущностей:

```python
async def _seed_department(session, name="Отдел тестирования") -> Department:
    """Создать отдел в тестовой БД."""
    ...

async def _seed_executor(session, name="Тестовый исполнитель", department_id=None) -> Executor:
    """Создать исполнителя (опционально в отделе)."""
    ...

async def _seed_meeting(session, title="Тестовое совещание", participant_ids=None) -> Meeting:
    """Создать совещание."""
    ...

async def _seed_item(session, topic="Тестовая задача", **kwargs) -> Item:
    """Создать задачу."""
    ...
```

---

## Блок 3: Безопасность — ВЫСОКИЙ ПРИОРИТЕТ

### 3.1. Добавить `iat` claim в JWT-токены

**Файл:** `backend/app/security.py:32-36`

В функции `_create_token()` добавить поле `"iat"`:
```python
payload["iat"] = datetime.utcnow()
payload["exp"] = datetime.utcnow() + expires_delta
```

Это база для будущей инвалидации токенов при смене пароля (проверка `iat < password_changed_at`).

### 3.2. Ограничить длину login-идентификатора

**Файл:** `backend/app/schemas/auth.py:12`

```python
identifier: str = Field(..., max_length=255, description="Логин, email или телефон")
```

Нужен импорт `Field` из pydantic.

### 3.3. Предупреждение CORS + localhost в проде

**Файл:** `backend/app/main.py`, внутри `lifespan()` (после строки 88)

Добавить проверку:
```python
if not settings.DEBUG and "localhost" in settings.ALLOWED_ORIGINS:
    print("[security] ВНИМАНИЕ: ALLOWED_ORIGINS содержит localhost в не-debug режиме!", flush=True)
```

---

## Блок 4: Типизация — СРЕДНИЙ ПРИОРИТЕТ

### 4.1. Return type annotations для роутеров

**Файлы:** Все файлы в `backend/app/routers/*.py`

Для каждого endpoint-функции добавить возвращаемый тип (берётся из `response_model=`):

**Пример для meetings.py:**

| Функция | Строка | Добавить тип |
|---------|--------|-------------|
| `list_meetings` | 16 | `-> PaginatedResponse[MeetingResponse]` |
| `get_meeting` | 29 | `-> MeetingResponse` |
| `create_meeting` | 40 | `-> MeetingResponse` |
| `update_meeting` | 51 | `-> MeetingResponse` |
| `delete_meeting` | 63 | `-> None` |

Аналогично для остальных роутеров:

- **executors.py** — 5 функций (16,26,37,48,59)
- **users.py** — 4 функции (22,30,66,133)
- **statuses.py** — 3 функции (15,31,43)
- **items.py** — 5 функций
- **auth.py** — 4 функции
- **departments.py** — 4 функции
- **export.py** — 3 функции

**Итого:** ~33 функции, каждая получает одну строку с return type.

### 4.2. Починить пропущенные типы в сервисах и репозиториях

| Файл:Строка | Что исправить |
|-------------|---------------|
| `services/executor_service.py:12` | `sync_executor_name(user)` → `sync_executor_name(user: User)` |
| `repositories/meeting_repository.py:23` | `_base_query(self)` → `-> Select[tuple[Meeting]]` |
| `repositories/item_repository.py:25` | `_base_query(self)` → `-> Select[tuple[Item]]` |
| `services/csv_service.py:43` | `_sanitize_cell(value)` → `_sanitize_cell(value: Any) -> str` |
| `services/csv_service.py:85` | `executors: list` → `executors: list[Executor]` |
| `services/executor_service.py:44` | `_check_user_free(...)` → `-> User` |
| `schemas/item.py:19` | `from_executor(cls, executor)` → `from_executor(cls, executor: Executor)` |

---

## Блок 5: Документация — НИЗКИЙ ПРИОРИТЕТ

### 5.1. Обновить устаревшие ссылки на SQLite

**Файлы и строки:**
- `README.md` — найти упоминания SQLite/aiosqlite, заменить на PostgreSQL/asyncpg
- `docs/ARCHITECTURE.md` (строки ~9, ~35, ~112) — заменить SQLite→PostgreSQL
- `DEPLOY.md` (~104, ~110-111) — раздел бэкапа обновить с `cp protocol.db` на `pg_dump`

### 5.2. Добавить LICENSE файл

**Файл:** `LICENSE` в корне проекта

Рекомендация: MIT License (стандарт для internal-проектов с возможностью future open-source).

---

## Критерии приёмки (Definition of Done)

| Блок | Критерий |
|------|----------|
| CI/CD | PR в `beta` триггерит пайплейн; `pytest` проходит; `docker build` успешен |
| Тесты | `pytest --cov=app` показывает **минимум 55%** покрытия; все новые тесты green |
| Безопасность | `iat` в токенах; `max_length` на identifier; warning на localhost+CORS; **ни одного regression** в существующих тестах |
| Типизация | Все 33+ endpoint-функции имеют return type annotation; 7 внутренних функций пофикшены; ruff не выдаёт новых ошибок |
| Документация | Ноль упоминаний SQLite в README/ARCHITECTURE; DEPLOY.md имеет `pg_dump`; LICENSE присутствует |

## Порядок выполнения

1. **Блок 1 (CI/CD)** — сначала, чтобы следующие блоки проверялись автоматически
2. **Блок 2 (тесты)** — максимальный вклад в качество
3. **Блок 3 (безопасность)** — небольшие правки, высокий эффект
4. **Блок 4 (типизация)** — механическая работа, низкий риск
5. **Блок 5 (документация)** — в конце, чтобы не было конфликтов merge

Каждый блок коммитится отдельно с описанием в CHANGELOG.md по правилам CLAUDE.md (ветка `beta`).
