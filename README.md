# Протокол совещаний (Meeting Minutes)

Самостоятельно размещаемое (self-hosted) веб-приложение для ведения протоколов совещаний
и управления задачами — лёгкая альтернатива Excel и Google Sheets с ролевым доступом,
историей статусов, справочниками и экспортом в Excel/CSV.

> **Версия:** 2.7.0 · **Статус:** ✅ в продакшне · **Лицензия:** внутренний проект (self-hosted)

---

## 🎯 Цель проекта

Команды часто ведут задачи по итогам совещаний в разрозненных таблицах: теряется история,
нет единого источника правды, сложно фильтровать и разграничивать доступ. Это приложение
даёт **одно место** для:

- фиксации задач по совещаниям с приоритетами и сроками;
- прозрачной **истории изменения статусов** (таймлайн);
- работы команды с **ролевым доступом** (наблюдатель / редактор / администратор);
- быстрого экспорта в Excel/CSV для отчётности и обмена.

Разворачивается одним `docker compose` в собственной инфраструктуре — данные не покидают
ваш сервер.

---

## ✨ Возможности

**Задачи и статусы**
- CRUD задач: тема, тикет, приоритет, состояние, срок, исполнители, привязка к совещанию
- Состояния: «в работе» / «отложено» / «закрыто»; индикация просроченных
- История статусов (таймлайн) с датами и комментариями
- Фильтрация и полнотекстовый поиск (тема, тикет, исполнитель), сортировка по колонкам
- Массовые действия (bulk): смена состояния и удаление выделенных задач

**Справочники и совещания**
- Отделы и исполнители (с привязкой исполнителя к учётной записи)
- Совещания с участниками; группировка задач по совещанию

**Доступ и безопасность**
- Аутентификация по логину / email / телефону (JWT: access + refresh, ротация)
- Роли: **viewer** (чтение), **editor** (CRUD), **admin** (+ управление пользователями)
- Обязательная смена пароля при первом входе; авто-создание первого администратора
- Журнал аудита значимых действий; rate limiting на auth (защита от брутфорса)

**Обмен данными и UX**
- Экспорт CSV и XLSX, импорт CSV (UTF-8 BOM — корректно открывается в Excel)
- Тёмная тема, оптимизированные стили для печати
- Сохранение фильтров и состояния между перезагрузками (localStorage)

---

## 🛠️ Технологический стек

### Backend
- **Python 3.12+**, **FastAPI** (async)
- **SQLAlchemy 2.0** (строго асинхронный режим) + **asyncpg**
- **PostgreSQL 16** (в тестах — in-memory SQLite через aiosqlite)
- **Alembic** — версионирование схемы (миграции)
- **Pydantic v2** — валидация на границах системы
- Аутентификация: **python-jose** (JWT HS256) + **bcrypt**
- Экспорт Excel: **openpyxl**

### Frontend
- **Svelte 5** (Runes: `$state` / `$derived` / `$effect`) на **SvelteKit** (adapter-static, SPA)
- **Vite**, **TypeScript** (strict)
- **Tailwind CSS** 3.4, headless-компоненты **Bits UI**, иконки **Lucide**
- Состояние — классы-сторы в `*.svelte.ts`; типы генерируются из OpenAPI

### Качество и инфраструктура
- **Ruff** (линт) и **Pyright** (типы) для backend
- **pytest** (backend) и **Vitest** (frontend)
- **pre-commit** (ruff + svelte-check), **GitHub Actions** CI
- **Docker** multi-stage (фронтенд собирается и встраивается в backend-образ)

---

## 🧱 Архитектура

Строгое слоистое разделение backend — бизнес-логики в роутерах нет:

```
HTTP (routers) → services (бизнес-логика) → repositories (CRUD) → models (SQLAlchemy)
                         ↕ schemas (Pydantic, валидация на границе)
```

В продакшне один контейнер отдаёт и API, и собранный Svelte-SPA на `:8000` (фронтенд
встроен в `static/`), рядом — контейнер PostgreSQL. На фронтенде список задач фильтруется/
сортируется на клиенте (источник истины для UI), серверные фильтры — для API/экспорта.

---

## 📁 Структура проекта

```
Protocol/
├── backend/
│   ├── app/
│   │   ├── models/            # SQLAlchemy-модели (item, status, executor, department,
│   │   │                      #   meeting, user, audit_log, M2M-таблицы)
│   │   ├── schemas/           # Pydantic-схемы (валидация запросов/ответов)
│   │   ├── repositories/      # CRUD-слой (generic BaseRepository + конкретные)
│   │   ├── services/          # Бизнес-логика (items, status, meeting, auth, csv, audit…)
│   │   ├── routers/           # HTTP-слой (auth, users, departments, executors,
│   │   │                      #   items, statuses, meetings, export)
│   │   ├── middleware/        # Rate limiting
│   │   ├── utils/             # Константы, идентификаторы, время
│   │   ├── config.py          # Настройки (pydantic-settings)
│   │   ├── database.py        # Async engine + сессия (get_db)
│   │   ├── dependencies.py    # Авторизация (get_current_user / require_editor / admin)
│   │   ├── security.py        # JWT + bcrypt
│   │   ├── logging_config.py  # Структурированное логирование
│   │   └── main.py            # Точка входа FastAPI (+ раздача SPA)
│   ├── alembic/               # Миграции БД
│   ├── tests/                 # pytest (SQLite; в CI также реальный PostgreSQL)
│   ├── pyproject.toml         # Зависимости + конфиг ruff/pytest/pyright
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/           # API-клиент (fetch + авто-refresh токена) и типы
│   │   │   ├── components/    # Svelte-компоненты (ui / items / refs / common)
│   │   │   ├── stores/        # Runes-сторы (items, filters, selection, auth, theme…)
│   │   │   └── utils/         # date / format / constants / itemFilter
│   │   ├── routes/            # SvelteKit-страницы (/, /login, /meetings, /refs, /admin…)
│   │   ├── app.html · app.css # Шаблон и Tailwind
│   ├── package.json
│   ├── vite.config.ts · vitest.config.ts · svelte.config.js · tailwind.config.ts
│   └── tsconfig.json
│
├── scripts/                   # seed-данные / утилиты
├── deploy/                    # nginx.conf (reverse-proxy для прода)
├── docs/                      # ARCHITECTURE.md, AUDIT_v2.7.0.md
├── .github/workflows/ci.yml   # CI: ruff, pyright, pytest (SQLite+PG), svelte-check, vitest, docker build
├── docker-compose.yml         # Базовый стек (backend + postgres, порт 8000)
├── docker-compose.dev.yml     # Dev: backend hot-reload + frontend HMR (5173)
├── docker-compose.prod.yml    # Prod: порт 127.0.0.1 (за Nginx), .env обязателен
├── docker-compose.local-prod.yml  # Локальный прод: + nginx (HTTPS через mkcert)
├── Dockerfile · Dockerfile.dev
├── .pre-commit-config.yaml · .env.example
├── CHANGELOG.md · DEPLOY.md · CLAUDE.md · LICENSE
└── README.md
```

---

## 📋 Требования

- **Docker** 20.10+ и Docker Compose — рекомендуемый способ запуска
- Для запуска без Docker: **Python 3.12+**, **Node.js 20+**, доступный **PostgreSQL 16**

---

## 🚀 Способы запуска

Перед запуском в проде/деплое создайте `.env` (см. [Конфигурация](#-конфигурация)):
```bash
cp .env.example .env   # и задайте SECRET_KEY, POSTGRES_PASSWORD, FIRST_ADMIN_*
```

### Вариант 1 — базовый стек (рекомендуется для локального прогона)
Backend + PostgreSQL в одном `compose`; фронтенд уже встроен в образ.
```bash
docker compose up -d --build
# Приложение:   http://localhost:8000
# Swagger UI:    http://localhost:8000/api/docs
```

### Вариант 2 — режим разработки (hot-reload)
Backend с авто-перезагрузкой (8000) и фронтенд с HMR (5173) — раздельно.
```bash
docker compose -f docker-compose.dev.yml up
# Фронтенд (HMR): http://localhost:5173
# API + Swagger:  http://localhost:8000/api/docs
```

### Вариант 3 — продакшн (за Nginx)
Порт привязан к `127.0.0.1`, публичный доступ — через reverse-proxy (`deploy/nginx.conf`).
`.env` обязателен. Подробности — в [DEPLOY.md](DEPLOY.md).
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Вариант 4 — локально без Docker
Нужен запущенный PostgreSQL и переменная `DATABASE_URL`.

**Backend**
```bash
cd backend
pip install -e ".[dev]"                 # проект на pyproject.toml
export DATABASE_URL=postgresql+asyncpg://protocol:protocol@localhost:5432/protocol
alembic upgrade head                     # или оставьте миграции на старте (по умолчанию)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173 (проксирует /api на :8000)
```

---

## ⚙️ Конфигурация

Переменные окружения (значения по умолчанию — в `app/config.py`, пример — в `.env.example`):

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `DATABASE_URL` | строка подключения PostgreSQL (asyncpg) | `postgresql+asyncpg://protocol:protocol@localhost:5432/protocol` |
| `POSTGRES_PASSWORD` | пароль БД (используется compose) | `protocol` |
| `SECRET_KEY` | подпись JWT — **обязателен в проде** (`openssl rand -hex 32`) | dev-заглушка (в проде старт прерывается) |
| `DEBUG` | режим отладки / SQL-эхо | `False` |
| `ALLOWED_ORIGINS` | разрешённые CORS-источники (через запятую) | `http://localhost:5173,http://localhost:8000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | срок жизни access-токена | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | срок жизни refresh-токена | `7` |
| `FIRST_ADMIN_USERNAME` / `FIRST_ADMIN_PASSWORD` | первый админ (создаётся при пустой БД) | `admin` / `admin` |
| `RUN_MIGRATIONS_ON_STARTUP` | применять Alembic-миграции при старте | `True` |

### Первый вход
При первом запуске с пустой таблицей пользователей автоматически создаётся администратор
(`FIRST_ADMIN_USERNAME` / `FIRST_ADMIN_PASSWORD`) с флагом обязательной смены пароля — при
входе система потребует задать новый. **Смените дефолтные значения до первого запуска в проде.**

---

## 📖 API

Интерактивная документация (после запуска):
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`

Основные группы эндпоинтов (полный список и схемы — в Swagger):
```
POST   /api/auth/login | /api/auth/refresh        # вход и обновление токена
GET    /api/auth/me · POST /api/auth/change-password

GET/POST/PATCH/DELETE  /api/items                 # задачи (+ /items/{id})
GET/POST   /api/items/{id}/statuses · DELETE /api/statuses/{id}   # история статусов

GET/POST/.. /api/departments · /api/executors      # справочники
GET/POST/.. /api/meetings                          # совещания
GET/POST/PATCH/DELETE /api/users                   # пользователи (только admin)

POST   /api/export/csv · /api/export/xlsx · /api/import/csv   # обмен данными

GET    /health · /health/detailed                  # health-check (+ статус БД, версия миграции)
```

### Роли и доступ
| Роль | Права |
|------|-------|
| `viewer` | чтение задач, справочников, совещаний |
| `editor` | + создание/изменение/удаление задач, статусов, справочников, совещаний |
| `admin` | + управление пользователями и ролями |

---

## 🧪 Тестирование и качество

```bash
# Backend
cd backend
ruff check app/         # линт
pyright app/            # проверка типов
pytest                  # тесты (in-memory SQLite); в CI также прогон на реальном PostgreSQL

# Frontend
cd frontend
npm run check           # svelte-check (типы)
npm run test            # Vitest

# Pre-commit (ruff + svelte-check) — по желанию
pip install pre-commit && pre-commit install
```

**CI (GitHub Actions)** на push/PR в `beta` и `main`: `ruff` + `pyright`, `pytest`
(SQLite и PostgreSQL), `svelte-check` + `vitest`, а на `main` — сборка production-образа.

---

## 🐳 Деплой

Подробная инструкция (Nginx, TLS, бэкапы `pg_dump`, обновление) — в [DEPLOY.md](DEPLOY.md).
Кратко:
```bash
cp .env.example .env    # заполнить SECRET_KEY, POSTGRES_PASSWORD, FIRST_ADMIN_*
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 📚 Документация

- [CHANGELOG.md](CHANGELOG.md) — история версий (Keep a Changelog)
- [DEPLOY.md](DEPLOY.md) — развёртывание в продакшн
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — архитектурные решения
- [docs/AUDIT_v2.7.0.md](docs/AUDIT_v2.7.0.md) — аудит кодовой базы и план улучшений
- [CLAUDE.md](CLAUDE.md) — соглашения по версионированию и git-флоу

---

## 🧭 Соглашения разработки

- Backend — PEP 8 + Ruff; типизация под Pyright (без `Any` на границах)
- Frontend — TypeScript (strict) + Svelte 5 Runes; Prettier
- Комментарии в коде — на русском; имена — на английском
- Логирование — через `logging` (структурированный формат), не `print`
- Ветвление: фичи в `beta` → squash-PR в `main` (стабильная). Подробности — в `CLAUDE.md`

---

## 👤 Контакты

Разработка: **SckraT** · GitHub: <https://github.com/SckraT>

---

**Версия:** 2.7.0 · **Обновлено:** 2026-06-06
