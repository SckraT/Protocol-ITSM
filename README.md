# Протокол совещаний (Meeting Minutes) v2.0

Минималистичное веб-приложение для ведения протоколов совещаний и управления задачами — самостоятельно размещаемая альтернатива Excel и Google Sheets.

## 🎯 Возможности

- **CRUD задач** — создание, редактирование, удаление задач
- **Управление статусами** — отслеживание состояния (в работе / отложено / закрыто)
- **История статусов (Таймлайн)** — полная запись всех изменений статусов
- **Справочники** — управление отделами и исполнителями
- **Фильтрация и поиск** — по отделу, исполнителю, приоритету, полнотекстовый поиск
- **Массовые действия** — выделение чекбоксами, bulk-операции (смена статуса, удаление)
- **Экспорт/Импорт** — CSV с поддержкой UTF-8 BOM для Excel
- **Сохранение состояния** — восстановление фильтров и открытой задачи после перезагрузки
- **Темная тема** — переключение Light/Dark mode
- **Печать** — оптимизированные стили для печати

## 🛠️ Технологический стек

### Backend
- **Фреймворк:** FastAPI 0.115.0+
- **ORM:** SQLAlchemy 2.0.36+ (асинхронный режим)
- **БД:** PostgreSQL 16 (asyncpg в проде; в тестах — in-memory SQLite через aiosqlite)
- **Миграции:** Alembic с версионированием
- **Валидация:** Pydantic v2
- **API:** OpenAPI (Swagger доступен на `/api/docs`)

### Frontend
- **Фреймворк:** Svelte 5 + Vite
- **Стили:** Tailwind CSS 3.4.0+
- **UI компоненты:** Bits UI (Headless)
- **Иконки:** Lucide Svelte
- **Язык:** TypeScript (типизация из OpenAPI)

## 📋 Требования

- **Python:** 3.12+
- **Node.js:** 18+ (для фронтенда)
- **Docker:** 20.10+ (опционально, для контейнеризации)
- **Git:** для версионирования кода

## 🚀 Быстрый старт

### Локальное развитие (с Docker Compose)

```bash
cd D:\Protocol

# Запустить оба сервиса (backend на 8000, frontend на 5173)
docker-compose -f docker-compose.dev.yml up

# В браузере открыть:
# - Фронтенд: http://localhost:5173
# - API Swagger: http://localhost:8000/api/docs
```

### Локальное развитие (без Docker)

#### Backend
```bash
cd backend

# Установить зависимости
pip install -r requirements.txt

# Миграции БД
alembic upgrade head

# Запустить сервер (автозагрузка на изменения)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev-сервер (HMR включен)
npm run dev
```

## 📁 Структура проекта

```
Protocol/
├── backend/
│   ├── app/
│   │   ├── models/           # SQLAlchemy модели БД
│   │   ├── schemas/          # Pydantic валидация
│   │   ├── repositories/     # CRUD слой
│   │   ├── services/         # Бизнес-логика
│   │   ├── routers/          # HTTP эндпоинты
│   │   ├── main.py           # FastAPI приложение
│   │   ├── config.py         # Конфигурация
│   │   └── database.py       # SQLAlchemy engine + session
│   ├── alembic/              # Миграции БД
│   ├── tests/                # pytest тесты
│   ├── pyproject.toml        # Зависимости
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/          # API клиент
│   │   │   ├── components/   # Svelte компоненты
│   │   │   ├── stores/       # Svelte Runes состояние
│   │   │   └── utils/        # Утилиты
│   │   ├── routes/           # SvelteKit роуты
│   │   ├── app.html          # HTML шаблон
│   │   └── app.css           # Tailwind
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── svelte.config.js
│
├── data/                     # Каталог данных (legacy v1; в v2 БД — в Docker volume postgres-data)
├── scripts/                  # Миграция данных, seed-ы
├── docs/                     # Архитектурная документация
├── docker-compose.yml        # Production
├── docker-compose.dev.yml    # Development
├── Dockerfile                # Multi-stage build
├── CHANGELOG.md              # История версий
├── BACKLOG.md                # Дорожная карта задач
└── README.md                 # Этот файл
```

## 📖 API Документация

Полная интерактивная документация доступна после запуска:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

Основные эндпоинты:
```
GET    /api/items                    # Список задач
POST   /api/items                    # Создать задачу
GET    /api/items/{id}               # Получить задачу
PATCH  /api/items/{id}               # Обновить задачу
DELETE /api/items/{id}               # Удалить задачу

POST   /api/items/{id}/statuses      # Добавить новый статус
GET    /api/items/{id}/statuses      # История статусов

GET    /api/departments              # Список отделов
POST   /api/departments              # Создать отдел
# и т.д.

POST   /api/export/csv               # Экспорт в CSV
POST   /api/import/csv               # Импорт из CSV
```

## 🧪 Тестирование

```bash
# Backend тесты
cd backend
pytest -v --cov=app tests/

# Frontend тесты
cd frontend
npm run test
```

## 🐳 Docker Production

```bash
# Собрать образ
docker build -t protocol:2.0 .

# Запустить контейнер
docker run -p 8000:8000 -v $(pwd)/data:/app/data protocol:2.0

# Или через Compose (production)
docker-compose up -d
```

## 📝 Разработка

### Соглашения кода

- **Backend:** Python 3.12+ PEP 8, Ruff линтер
- **Frontend:** TypeScript + Svelte 5, Prettier для форматирования
- **Комментарии:** Русский язык
- **Логирование:** Структурированное логирование через Python logging
- **Безопасность:** Ноль инлайн обработчиков, валидация на границах системы

### Подготовка PR

1. Создайте ветку от `main`: `git checkout -b feat/описание`
2. Внесите изменения и скоммитьте с чистыми сообщениями
3. Убедитесь, что тесты проходят: `pytest` / `npm test`
4. Обновите `CHANGELOG.md`
5. Создайте PR с описанием изменений

## 📚 Дополнительная документация

- [CHANGELOG.md](CHANGELOG.md) — история версий
- [BACKLOG.md](BACKLOG.md) — дорожная карта разработки (этапы 1-6)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — архитектурные решения (планируется)
- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) — миграция данных из v1 (планируется)

## 🔧 Troubleshooting

### Backend не стартует
```bash
# Проверить миграции
alembic current

# Пересоздать БД
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d --build
# Миграции применятся автоматически при старте приложения (lifespan)
```

### Frontend не видит API
Убедитесь, что backend запущен на `http://localhost:8000` и proxy в `vite.config.ts` настроен правильно.

### Ошибки CORS
Проверьте `app/main.py` — там должны быть разрешены `http://localhost:5173` и другие необходимые origins.

## 📄 Лицензия

Внутренний проект (Self-hosted).

## 👤 Контакты

Разработка: SckraT  
GitHub: https://github.com/SckraT

---

**Версия:** 2.0.0  
**Дата обновления:** 2026-06-01  
**Статус:** ✅ Этапы 1–6 завершены (backend + frontend + Docker)

См. также: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
