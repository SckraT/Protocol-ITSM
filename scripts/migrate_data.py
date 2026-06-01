"""
Скрипт миграции данных v1 → v2.
Переносит исполнителей из items.executors_json (JSON-массив ID) в таблицу item_executors (M2M).

Запуск (после alembic upgrade head):
    python scripts/migrate_data.py

Безопасно запускать повторно — использует INSERT OR IGNORE.
"""
import json
import sqlite3
import sys
from pathlib import Path

# Путь к БД — ищем относительно корня проекта
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "protocol.db"


def migrate() -> None:
    """Переносит данные executors_json → item_executors."""
    if not DB_PATH.exists():
        print(f"ОШИБКА: БД не найдена по пути {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Проверяем, что таблица item_executors уже существует
        existing_tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "item_executors" not in existing_tables:
            print("ОШИБКА: Таблица item_executors не найдена. Сначала запустите 'alembic upgrade head'.", file=sys.stderr)
            sys.exit(1)

        # Читаем все задачи с заполненным executors_json
        rows = conn.execute(
            "SELECT id, executors_json FROM items WHERE executors_json IS NOT NULL AND executors_json != '[]'"
        ).fetchall()

        print(f"Найдено задач с исполнителями: {len(rows)}")

        inserted = 0
        skipped = 0
        errors = 0

        for row in rows:
            item_id = row["id"]
            ej = row["executors_json"]

            try:
                ids = json.loads(ej)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"  ПРОПУСК задача #{item_id}: ошибка парсинга JSON — {e}")
                skipped += 1
                continue

            if not isinstance(ids, list):
                print(f"  ПРОПУСК задача #{item_id}: executors_json не является массивом")
                skipped += 1
                continue

            for exec_id in ids:
                if not isinstance(exec_id, int):
                    print(f"  ПРЕДУПРЕЖДЕНИЕ задача #{item_id}: нецелочисленный ID исполнителя {exec_id!r}")
                    continue

                # Проверяем существование исполнителя
                exists = conn.execute(
                    "SELECT 1 FROM executors WHERE id = ?", (exec_id,)
                ).fetchone()

                if not exists:
                    print(f"  ПРЕДУПРЕЖДЕНИЕ задача #{item_id}: исполнитель #{exec_id} не найден в справочнике, пропускаем")
                    continue

                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO item_executors (item_id, executor_id) VALUES (?, ?)",
                        (item_id, exec_id),
                    )
                    inserted += 1
                except sqlite3.IntegrityError as e:
                    print(f"  ОШИБКА задача #{item_id} исполнитель #{exec_id}: {e}")
                    errors += 1

        conn.commit()

        print(f"\nМиграция завершена:")
        print(f"  Добавлено записей в item_executors: {inserted}")
        print(f"  Пропущено задач: {skipped}")
        print(f"  Ошибок: {errors}")

        # Верификация
        total_in_table = conn.execute("SELECT COUNT(*) FROM item_executors").fetchone()[0]
        print(f"  Всего записей в item_executors: {total_in_table}")

    except Exception as e:
        conn.rollback()
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
