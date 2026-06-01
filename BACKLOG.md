# Backlog v2.0 — Дорожная карта переписывания проекта

Полный список работ для переписывания Meeting Minutes с нуля на современный стек.  
Отметки: `[ ]` — в планах, `[x]` — сделано (см. [CHANGELOG.md](CHANGELOG.md)).  
Стадия: **✅ Этапы 1–6 завершены. Контейнер собирается и работает (healthy).**

---

## 📋 Этап 1: Проектирование и Бэкенд (Backend Setup & Architecture) ✅

### Инициализация проекта
- [x] 1.1. Инициализация git-репозитория, структура папок (backend/, frontend/, data/, scripts/, docs/)
- [x] 1.2. Настройка линтеров: Ruff для Python (`ruff.toml`)
- [x] 1.3. Создание `.gitignore`, `.editorconfig`
- [ ] 1.4. Инициализация GitHub Actions (опционально) или локальных pre-commit hooks

### Backend структура и конфигурация
- [x] 1.5. Создание `backend/pyproject.toml` с зависимостями:
  - FastAPI 0.115.0+, Uvicorn, SQLAlchemy 2.0.36+ с asyncio, aiosqlite, Alembic, Pydantic v2, openpyxl
  - pytest, pytest-asyncio, httpx (для тестов)
- [x] 1.6. Создание `backend/alembic.ini` и `alembic/env.py` (async-режим)
- [x] 1.7. Создание `backend/app/config.py` (Pydantic Settings)
- [x] 1.8. Создание `backend/app/database.py` (AsyncSession, engine с aiosqlite, get_db с commit/rollback)
- [x] 1.9. Создание `backend/app/__init__.py`

### SQLAlchemy модели БД
- [x] 1.10. Создание `backend/app/models/base.py` (DeclarativeBase, mapped_column стиль)
- [x] 1.11. Создание `backend/app/models/item.py`
- [x] 1.12. Создание `backend/app/models/status.py`
- [x] 1.13. Создание `backend/app/models/department.py`
- [x] 1.14. Создание `backend/app/models/executor.py`
- [x] 1.15. Создание `backend/app/models/item_executor.py` (M2M Table-объект)
- [x] 1.16. Настройка связей (relationships, cascade delete правила)

### Pydantic схемы валидации
- [x] 1.17. Создание `backend/app/schemas/item.py`
- [x] 1.18. Создание `backend/app/schemas/status.py`
- [x] 1.19. Создание `backend/app/schemas/department.py`
- [x] 1.20. Создание `backend/app/schemas/executor.py`
- [x] 1.21. Создание `backend/app/schemas/common.py` (PaginatedResponse[T], StateEnum, PriorityEnum)
- [x] 1.22. Настройка enums для state/priority

### Слой репозиториев
- [x] 1.23. Создание `backend/app/repositories/base.py` (BaseRepository[T])
- [x] 1.24. Создание `backend/app/repositories/item_repository.py`
- [x] 1.25. Создание `backend/app/repositories/status_repository.py`
- [x] 1.26. Создание `backend/app/repositories/department_repository.py`
- [x] 1.27. Создание `backend/app/repositories/executor_repository.py`

### Слой сервисов (бизнес-логика)
- [x] 1.28. Создание `backend/app/services/item_service.py`
- [x] 1.29. Создание `backend/app/services/status_service.py`
- [x] 1.30. Создание `backend/app/services/department_service.py`
- [x] 1.31. Создание `backend/app/services/executor_service.py`
- [x] 1.32. Создание `backend/app/services/csv_service.py`

### HTTP роутеры (API эндпоинты)
- [x] 1.33. Создание `backend/app/routers/items.py` (GET/POST/PATCH/DELETE + фильтрация)
- [x] 1.34. Создание `backend/app/routers/statuses.py`
- [x] 1.35. Создание `backend/app/routers/departments.py`
- [x] 1.36. Создание `backend/app/routers/executors.py`
- [x] 1.37. Создание `backend/app/routers/export.py` (CSV/XLSX экспорт-импорт)

### FastAPI приложение и инициализация
- [x] 1.38. Создание `backend/app/main.py` (lifespan с Alembic, CORS, StaticFiles, /health)
- [x] 1.39. Создание `backend/app/utils/constants.py`

### Миграции БД и первая инициализация
- [x] 1.40. Создание начальной миграции `alembic/versions/20260601_0001_initial_schema.py`
- [x] 1.41. Миграция включает WAL-режим и foreign_keys, ON DELETE CASCADE/SET NULL
- [x] 1.42. Создание скрипта миграции данных `scripts/migrate_data.py`
- [ ] 1.43. Создание seed-скрипта для dev (`scripts/seed.py`) с test-данными

### Тестирование Backend
- [x] 1.44. Создание `backend/tests/conftest.py` (in-memory SQLite, ASGI client)
- [x] 1.45. Тесты API: `test_departments_api.py`, `test_items_api.py`
- [ ] 1.46. Тесты сервисов: `test_csv_service.py`
- [x] 1.47. Настройка pytest в pyproject.toml (asyncio_mode=auto)

---

## 🎨 Этап 2: Фронтенд-каркас (Frontend Setup & Scaffolding) ✅

### Инициализация Svelte 5 проекта
- [x] 2.1. Инициализация Svelte 5 + SvelteKit проекта
- [x] 2.2. Установка зависимостей: svelte 5, kit, adapter-static, tailwindcss, bits-ui, lucide-svelte, clsx, tailwind-merge, openapi-typescript, prettier
- [x] 2.3. TypeScript strict режим (tsconfig.json)
- [x] 2.4. Tailwind CSS + PostCSS (tailwind.config.ts, postcss.config.js)
- [x] 2.5. SvelteKit с adapter-static (SPA-режим, fallback index.html)

### Конфигурация инструментов
- [x] 2.6. `frontend/vite.config.ts` (sveltekit plugin, proxy /api → :8000, порт 5173)
- [x] 2.7. `frontend/tailwind.config.ts` (darkMode data-theme, CSS-переменные тем)
- [x] 2.8. `frontend/svelte.config.js` (adapter-static → dist/)
- [x] 2.9. `frontend/.prettierrc`
- [x] 2.10. `frontend/tsconfig.json` (strict)

### Структура фронтенда
- [x] 2.11. `frontend/src/app.html` (+ предзагрузка темы для anti-FOUC)
- [x] 2.12. `frontend/src/app.css` (Tailwind + CSS-переменные Light/Dark из v1)
- [x] 2.13. Папки `frontend/src/lib/{api,components,stores,utils}`
- [x] 2.14. Папка `frontend/src/routes/`

### API клиент и типизация
- [x] 2.15. `frontend/src/lib/api/client.ts` (apiGet/Post/Patch/Put/Delete, ApiError, ApiUrl)
- [x] 2.16. `frontend/src/lib/api/{items,statuses,departments,executors,export}.ts`
- [x] 2.17. `frontend/src/lib/api/types.ts` (типы под v2-схемы) + скрипт generate-types

### Svelte Runes и состояние
- [x] 2.18. `items.svelte.ts` ($state all, $derived filtered/counts/overdueCount, оптимистичные update/remove с откатом)
- [x] 2.19. `filters.svelte.ts` ($state фильтры, персист в localStorage, сортировка)
- [x] 2.20. `selection.svelte.ts` (Set выбранных задач)
- [x] 2.21. `theme.svelte.ts` (Light/Dark, prefers-color-scheme, data-theme)
- [x] 2.22. `refs.svelte.ts` (отделы + исполнители, CRUD, группировка)
- [x] (доп.) `toast.svelte.ts` (уведомления)

### Базовые UI-компоненты
- [x] 2.23. `ui/Button.svelte` (варианты primary/secondary/danger/ghost)
- [x] 2.24. `ui/Input.svelte` ($bindable)
- [x] 2.25. `ui/Select.svelte` ($bindable)
- [x] 2.26. `ui/Modal.svelte` (нативный, Esc, клик по фону, a11y)
- [x] 2.27. `ui/Drawer.svelte` (slide-over, Esc, транзишены)
- [x] 2.28. `ui/Badge.svelte` (состояние/приоритет)
- [x] 2.29. `ui/Toast.svelte` (role=status, транзишены)
- [x] 2.30. `ui/Loader.svelte` (спиннер)

### Утилиты и константы
- [x] 2.31. `utils/date.ts` (fmtDate, today, dueInfo, isOverdue — портировано из v1)
- [x] 2.32. `utils/format.ts` (plural — рус. склонения, esc)
- [x] 2.33. `utils/constants.ts` (STATE_LABEL/BADGE/ORDER, PRIORITY_CONFIG)

### Главная разметка
- [x] 2.34. `routes/+layout.svelte` (header, nav, переключатель темы, Toast, загрузка данных, badge вкладки)
- [x] 2.35. `routes/+page.svelte` (дашборд + поиск + базовая таблица)
- [x] 2.36. `routes/refs/+page.svelte` (отделы + исполнители)
- [x] (доп.) `routes/+layout.ts` (SPA: ssr=false)

**Верификация:** `npm run check` → 0 ошибок, 0 предупреждений; `npm run build` → успешно, `dist/` с SPA fallback.

---

## 📊 Этап 3: Перенос бизнес-логики (Business Logic Migration) ✅

### Компоненты таблицы задач
- [x] 3.1. Создание `frontend/src/lib/components/items/ItemsTable.svelte`:
  - Таблица с thead, tbody
  - Рендер строк из `allItems` store
  - Сортировка, пагинация
- [x] 3.2. Создание `frontend/src/lib/components/items/ItemRow.svelte`:
  - Строка таблицы с полями (тема, тикет, приоритет, состояние, срок, исполнители)
  - Контекстное меню (три точки)
- [x] 3.3. Создание `frontend/src/lib/components/items/ItemDrawer.svelte`:
  - Drawer с полной информацией о задаче
  - Форма редактирования
  - Timeline справа (история статусов)
  - Кнопки (Сохранить, Отмена, Удалить)

### Форма и редактирование
- [x] 3.4. Создание `frontend/src/lib/components/items/ItemForm.svelte`:
  - Инпуты для всех полей (тема, тикет, приоритет, состояние, срок, исполнители)
  - Валидация перед отправкой
  - Обработка ошибок
- [x] 3.5. Создание `frontend/src/lib/components/items/StatusForm.svelte` (форма добавления статуса)
- [x] 3.6. Создание `frontend/src/lib/components/items/Timeline.svelte`:
  - Список статусов с датами и текстом
  - Кнопки удаления статусов

### Фильтрация и поиск
- [x] 3.7. Создание `frontend/src/lib/components/items/Filters.svelte`:
  - Dashboard-тайлы (Все / В работе / Отложено / Закрыто)
  - Расширенные фильтры (отдел, исполнитель, приоритет)
  - Кнопка «Сбросить»
- [x] 3.8. Создание `frontend/src/lib/components/common/SearchBar.svelte`:
  - Строка поиска с иконкой
  - Отправка в store при вводе
- [x] 3.9. Реализация фильтрации на уровне store (filter items в `filters.svelte.ts`)

### Массовые операции
- [x] 3.10. Создание `frontend/src/lib/components/items/BulkActions.svelte`:
  - Sticky floating panel внизу экрана
  - Checkbox для выбора задач
  - Кнопки (смена статуса, удаление, экспорт)
- [x] 3.11. Интеграция bulk-операций в `ItemRow.svelte` и `ItemsTable.svelte`

### Справочники
- [x] 3.12. Создание `frontend/src/lib/components/refs/DepartmentsList.svelte`:
  - Список отделов с кнопками добавления/редактирования/удаления
  - Inline-редактирование
  - Счётчики исполнителей
- [x] 3.13. Создание `frontend/src/lib/components/refs/ExecutorsList.svelte`:
  - Группировка по отделам
  - CRUD операции
  - Счётчики задач
- [x] 3.14. Inline-строки справочников (логика объединена в DepartmentsList/ExecutorsList — отдельный RefItem не понадобился)

### Дополнительные компоненты
- [x] 3.15. Создание `frontend/src/lib/components/common/Dashboard.svelte` (если отдельный компонент)
- [x] 3.16. Создание `frontend/src/lib/components/common/Pagination.svelte` (навигация по страницам)
- [x] 3.17. Создание `frontend/src/lib/components/common/ConfirmDialog.svelte` (подтверждение операций)

### Интеграция с API
- [x] 3.18. Реализация загрузки данных в `items.svelte.ts`:
  - `loadItems()`, `loadDepartments()`, `loadExecutors()` — параллельные запросы
  - Обработка ошибок и состояний загрузки
- [x] 3.19. Реализация создания/редактирования/удаления в сервисах:
  - `createItem()`, `updateItem()`, `deleteItem()`
  - Оптимистичное обновление UI
  - Откат при ошибках
- [x] 3.20. Синхронизация состояния с URL query-параметрами:
  - Сохранение фильтров, сортировки, открытой задачи
  - Восстановление при загрузке страницы

---

## 💎 Этап 4: UX-полировка и Оптимистичный UI (Optimistic UI & Polish) ✅

### Оптимистичный UI
- [x] 4.1. Реализация оптимистичного обновления:
  - Изменения применяются к `$state` ДО запроса к серверу
  - Откат состояния при ошибке API
  - Показ спиннера или проверка статуса запроса
- [x] 4.2. Реализация откатов при ошибках сети:
  - Перехватчики ошибок в API клиенте
  - Откат `$state` если запрос упал
  - Toast-уведомление об ошибке
- [ ] 4.3. Retry-логика для временно недоступного API (отложено — не входит в паритет с v1):
  - Автоматический retry с экспоненциальной задержкой
  - Максимум 3 попытки

### Анимации и переходы
- [x] 4.4. Добавление Svelte `transition` директив:
  - fade, slide, scale для открытия/закрытия Drawer
  - transition для появления/исчезновения toast'ов
- [x] 4.5. Добавление `animate:flip` для списков при удалении/добавлении элементов

### Валидация и обработка ошибок
- [x] 4.6. Валидация данных на фронтенде перед отправкой:
  - Проверка обязательных полей
  - Форматирование дат
  - Мин/макс длины текста
- [x] 4.7. Отображение ошибок валидации:
  - Подсветка инпутов
  - Текст ошибки под полем
- [x] 4.8. Обработка ошибок сервера:
  - Парсинг ошибок из ответа API (422 validation errors)
  - Toast-уведомления с текстом ошибки

### Загрузка и спиннеры
- [x] 4.9. Добавление Loading-состояний:
  - Спиннер при загрузке таблицы
  - Блокировка кнопок при отправке формы
  - Скелеты для превью содержимого (опционально)
- [x] 4.10. Добавление Empty-состояния:
  - Сообщение «Нет задач» если таблица пуста
  - Иконка и текст помощи

### Доступность и UX-мелочи
- [x] 4.11. ARIA-атрибуты для скрин-ридеров:
  - `aria-label` для иконок
  - `aria-live` для toast'ов
  - `role` для кастомных компонентов
- [x] 4.12. Поддержка навигации клавиатурой:
  - Tab между полями формы
  - Esc закрывает Drawer и модалки
  - Enter в формах отправляет данные
- [x] 4.13. Фокус управление:
  - Фокус переходит в Drawer при открытии
  - Фокус возвращается на кнопку при закрытии

---

## 📤 Этап 5: Экспорт/Импорт и Системные фичи (Export/Import & System Features) ✅

### CSV экспорт
- [x] 5.1. Реализация CSV-экспорта на бэкенде (`csv_service.py`):
  - Форматирование строк, кодировка UTF-8 с BOM
  - Сериализация исполнителей (format: `Отдел — Имя`)
  - Массиво поля (JSON → текст)
- [x] 5.2. Создание роутера `/api/export/csv` в `routers/export.py`
- [x] 5.3. Добавление кнопки экспорта в UI и обработка скачивания

### CSV импорт
- [x] 5.4. Реализация CSV-импорта на бэкенде:
  - Парсинг CSV (обработка BOM, энкодинга)
  - Сопоставление исполнителей по имени
  - Создание недостающих записей
  - Импорт последнего статуса
- [x] 5.5. Создание роутера `POST /api/import/csv`
- [x] 5.6. Добавление кнопки импорта в UI, обработка загрузки, фидбэк пользователю

### Системные фичи
- [x] 5.7. Счётчик просроченных в `<title>` браузерной вкладки:
  - Использование Svelte `$effect` для реактивного обновления
  - `document.title = "..."`
- [x] 5.8. Переключатель темной темы (Light/Dark mode):
  - Сохранение выбора в localStorage
  - Применение `data-theme` атрибута
  - Поддержка `prefers-color-scheme` медиа-запроса
- [x] 5.9. Стили для печати (`@media print`):
  - Скрытие навигации, фильтров, кнопок
  - Раскрытие всех аккордеонов
  - Оптимизация цветов и шрифтов
  - Заголовок с датой печати
- [x] 5.10. Сохранение состояния приложения:
  - Фильтры → localStorage
  - Открытая задача (ID) → URL query-параметр
  - Размер страницы → localStorage

---

## 🐳 Этап 6: Упаковка и Развертывание (Dockerization & Deployment) ✅

### Docker и контейнеризация
- [x] 6.1. Создание/обновление `Dockerfile`:
  - Multi-stage build: Node stage (сборка фронтенда) → Python stage (запуск бэкенда)
  - Копирование собранного фронтенда в static/ папку бэкенда
  - Инициализация БД и миграций при старте
- [x] 6.2. Создание `docker-compose.yml` (production):
  - Сервис backend (image из Dockerfile, expose 8000)
  - Volume для данных (protocol.db)
  - Environment переменные
- [x] 6.3. Создание `docker-compose.dev.yml`:
  - Оба сервиса запущены локально для разработки
  - Frontend на 5173, backend на 8000
  - Bind-mounts для hot-reload
  - Volumes для node_modules и Python packages (опционально)
- [x] 6.4. Создание `.dockerignore`
- [x] 6.5. Обновление `.gitignore` (исключить build-артефакты, venv, node_modules)

### Документация
- [x] 6.6. Написание/обновление `README.md`:
  - Описание проекта
  - Требования и стек
  - Инструкции быстрого старта (Docker и без)
  - Структура папок
  - API документация
  - Troubleshooting
- [x] 6.7. Создание `docs/ARCHITECTURE.md`:
  - Архитектурные решения (почему FastAPI, почему Svelte 5)
  - Диаграммы (опционально)
  - Паттерны (repository, service, store patterns)
- [x] 6.8. Создание `docs/MIGRATION_GUIDE.md`:
  - Как мигрировали данные из v1 в v2
  - Описание скрипта migrate_data.py
  - Команды для применения миграции
- [x] 6.9. Обновление `CHANGELOG.md` с полной историей v2.0.0
- [ ] 6.10. Создание `DEVELOPER.md` (опционально, не требуется) с инструкциями для контрибьюторов

### Финальное тестирование
- [x] 6.11. Smoke-тесты функциональности:
  - Запуск через docker-compose ✅ (контейнер Up healthy)
  - API-эндпоинты возвращают корректные v2-структуры (PaginatedResponse, M2M-исполнители, статусы)
  - CSV-экспорт с UTF-8 BOM ✅, driver.sh ✅
  - БД пересоздана с нуля и наполнена тестовыми данными (scripts/seed.py)
- [ ] 6.12. Тестирование в разных браузерах (Chrome, Firefox, Safari) — ручное, не выполнялось
- [ ] 6.13. Тестирование на мобильных (адаптив, touch-события) — ручное, не выполнялось
- [x] 6.14. Тёмная тема и light/dark переключатель (реализовано + предзагрузка против FOUC)
- [ ] 6.15. Проверка производительности (lighthouse) — ручное, не выполнялось

### Постпроцесс
- [x] 6.16. Финальный review кода (исправлены build-блокеры backend: build-backend, alembic shadow, миграция)
- [x] 6.17. Обновление всех документов (README, ARCHITECTURE, MIGRATION_GUIDE, CHANGELOG, skill)
- [x] 6.18. Подготовка release notes (CHANGELOG 2.0.0)
- [ ] 6.19. Пометить коммит тагом `v2.0.0` — выполнить при коммите (по запросу)

---

## 📌 Ключевые правила реализации

1. **100% функциональность v1.0:** Все фичи должны работать как минимум как в старой версии (или лучше)
2. **Русские комментарии:** В коде всегда использовать русский язык
3. **CHANGELOG по каждому этапу:** После завершения этапа обновить CHANGELOG.md (до завершения всех этапов выпускаем версии pre-release)
4. **Type-Safety:** End-to-end типизация (OpenAPI → TypeScript), строгий режим TypeScript
5. **Минимализм UI:** Никаких лишних элементов, все действия в контекстном меню или Drawer
6. **Безопасность:** Ноль инлайн-обработчиков событий, автоматический санитайзинг Svelte
7. **Асинхронность:** Backend полностью асинхронный (async/await + asyncio)
8. **Сохранение состояния:** Фильтры, сортировка, открытая задача восстанавливаются после перезагрузки

---

## 🎉 Definition of Done

Проект v2.0.0 считается завершённым когда:
- ✅ Все 6 этапов реализованы
- ✅ Все unit-тесты проходят (backend + frontend)
- ✅ Smoke-тесты ручных flow'ов успешны
- ✅ Docker образ собирается и работает
- ✅ Документация полная и актуальная
- ✅ Нет критических багов и XSS-уязвимостей
- ✅ Производительность приемлема (Lighthouse > 90)
- ✅ v2.0.0 готова к использованию в production
