# Руководство по миграции v1 → v2.0

Переписывание сохраняет 100% функциональности и **все данные** v1. Главное изменение
схемы — нормализация исполнителей: колонка `items.executors_json` (JSON-массив ID)
заменена на ассоциативную таблицу `item_executors` (M2M).

## Что переносится

- Все задачи (тема, тикет, приоритет, состояние, срок, дата создания)
- Все статусы с датами и примечаниями
- Все отделы и исполнители
- Связи задача ↔ исполнитель (из `executors_json` → `item_executors`)

## Перед началом

1. **Остановите приложение** (если запущено в Docker):
   ```bash
   docker compose down
   ```
2. **Сделайте резервную копию БД:**
   ```bash
   cp data/protocol.db data/protocol.db.backup
   ```

## Шаги миграции

### 1. Применить схему v2 (Alembic)

Создаёт таблицу `item_executors` и приводит схему к версии v2.

```bash
cd backend
python -m alembic upgrade head
cd ..
```

> URL базы берётся из `Settings` (`DB_PATH`/`DATABASE_URL`). По умолчанию это
> `data/protocol.db` в корне проекта.

### 2. Перенести данные исполнителей

Скрипт читает `items.executors_json`, парсит ID и наполняет `item_executors`.

```bash
python scripts/migrate_data.py
```

Свойства скрипта:

- Использует прямой доступ через `sqlite3` (не зависит от ORM).
- `INSERT OR IGNORE` — **безопасно запускать повторно** (идемпотентно).
- Проверяет существование каждого `executor_id`; отсутствующих пропускает с предупреждением.
- В конце печатает сводку: добавлено / пропущено / ошибок и общее число связей.

Пример вывода:

```
Найдено задач с исполнителями: 42
Миграция завершена:
  Добавлено записей в item_executors: 87
  Пропущено задач: 0
  Ошибок: 0
  Всего записей в item_executors: 87
```

### 3. Проверить целостность

Сумма длин всех `executors_json`-массивов должна совпасть с числом строк в
`item_executors`:

```bash
python -c "import sqlite3,json; c=sqlite3.connect('data/protocol.db'); \
js=sum(len(json.loads(r[0])) for r in c.execute(\"SELECT executors_json FROM items WHERE executors_json IS NOT NULL AND executors_json!='[]'\")); \
m=c.execute('SELECT COUNT(*) FROM item_executors').fetchone()[0]; \
print('executors_json:',js,' item_executors:',m,' OK' if js==m else ' РАСХОЖДЕНИЕ')"
```

### 4. Запустить v2

```bash
docker compose up -d --build
curl http://localhost:8000/health        # {"status":"ok",...}
curl http://localhost:8000/api/items      # PaginatedResponse с исполнителями
```

Откройте http://localhost:8000 и убедитесь, что задачи, статусы и исполнители на месте.

## Откат

Если что-то пошло не так — восстановите резервную копию:

```bash
docker compose down
cp data/protocol.db.backup data/protocol.db
```

## Примечания

- Колонка `executors_json` **не удаляется** — новый ORM её просто игнорирует
  (читает исполнителей через `item_executors`). Это упрощает откат.
- Для чистой установки (без данных v1) шаг 2 не нужен — таблицы создаются пустыми
  при `alembic upgrade head`.
