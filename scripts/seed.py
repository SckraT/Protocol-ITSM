"""
Наполнение БД тестовыми данными (v2.0).

Создаёт отделы, исполнителей, задачи (со связями M2M через item_executors)
и историю статусов. Перед вставкой очищает существующие данные — скрипт
предназначен для тестовой/демо-базы.

Запуск (после alembic upgrade head):
    python scripts/seed.py
"""
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "protocol.db"

# ── Тестовые данные ──────────────────────────────────────────────────────────

DEPARTMENTS = ["ИТ-инфраструктура", "Разработка", "Сопровождение", "Безопасность"]

# (имя исполнителя, индекс отдела в DEPARTMENTS или None)
EXECUTORS = [
    ("Иванов И.И.", 0),
    ("Петров П.П.", 0),
    ("Сидорова А.В.", 1),
    ("Кузнецов Д.С.", 1),
    ("Смирнова Е.А.", 2),
    ("Орлов М.Н.", 2),
    ("Волков Р.К.", 3),
    ("Фёдоров без отдела", None),
]

# (тема, тикет, приоритет, состояние, смещение срока в днях, [индексы исполнителей], [(смещение статуса, заметка)])
ITEMS = [
    ("Обновить мониторинг серверов", "TASK-1001", "high", "in_progress", 5, [0, 1], [(-2, "Развёрнут Zabbix-агент"), (-1, "Настроены триггеры")]),
    ("Интеграция с 1С", "TASK-1002", "medium", "in_progress", 12, [2, 3], [(-3, "Согласован формат обмена")]),
    ("Настройка резервного копирования", "TASK-1003", "high", "in_progress", -3, [0], [(-5, "Выбрано ПО"), (-2, "Тестовый бэкап выполнен")]),
    ("Тестирование API платёжного шлюза", "TASK-1004", "medium", "postponed", 20, [3], [(-1, "Ожидаем доступы от вендора")]),
    ("Документирование процессов ОПО", "TASK-1005", "low", "in_progress", 30, [4, 5], []),
    ("Оптимизация запросов к БД", "TASK-1006", "high", "in_progress", 2, [3], [(0, "Найдены медленные запросы")]),
    ("Миграция почтового сервера", "TASK-1007", "medium", "closed", -10, [0, 1], [(-12, "Подготовлен новый сервер"), (-10, "Миграция завершена")]),
    ("Обучение персонала ИБ", "TASK-1008", "low", "postponed", 45, [6], []),
    ("Проверка уязвимостей периметра", "TASK-1009", "high", "in_progress", 1, [6], [(-1, "Сканирование запущено")]),
    ("Разработка дашборда метрик", "TASK-1010", "medium", "in_progress", 15, [2, 3], [(-2, "Сверстан макет")]),
    ("Настройка CI/CD пайплайна", "TASK-1011", "high", "in_progress", 7, [3], [(-1, "Поднят раннер")]),
    ("Анализ логов инцидента", "TASK-1012", "high", "closed", -5, [4], [(-6, "Собраны логи"), (-5, "Причина установлена")]),
    ("Инвентаризация лицензий ПО", "TASK-1013", "low", "in_progress", 25, [5], []),
    ("Подготовка к аудиту", "TASK-1014", "medium", "postponed", 18, [6, 4], [(-2, "Запрошены документы")]),
    ("Рефакторинг модуля отчётов", "TASK-1015", "low", "in_progress", 40, [2], [(-1, "Выделены зоны рефакторинга")]),
    ("Развёртывание приложения на стенде", "TASK-1016", "medium", "closed", -7, [0, 3], [(-8, "Стенд подготовлен"), (-7, "Приложение развёрнуто")]),
    ("Тестирование отказоустойчивости", "TASK-1017", "high", "in_progress", 3, [0, 1], [(0, "Сценарии отказа описаны")]),
    ("Просроченная задача без статусов", "TASK-1018", "high", "in_progress", -15, [7], []),
]


def seed() -> None:
    if not DB_PATH.exists():
        print(f"ОШИБКА: БД не найдена по пути {DB_PATH}. Сначала запустите 'alembic upgrade head'.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    today = date.today()

    try:
        # Очистка существующих данных (тестовая база)
        for table in ("item_executors", "statuses", "items", "executors", "departments"):
            conn.execute(f"DELETE FROM {table}")

        # Отделы
        dept_ids: list[int] = []
        for name in DEPARTMENTS:
            cur = conn.execute(
                "INSERT INTO departments (name, created_at) VALUES (?, ?)", (name, now)
            )
            dept_ids.append(cur.lastrowid)

        # Исполнители
        exec_ids: list[int] = []
        for name, dept_idx in EXECUTORS:
            dept_id = dept_ids[dept_idx] if dept_idx is not None else None
            cur = conn.execute(
                "INSERT INTO executors (name, department_id, created_at) VALUES (?, ?, ?)",
                (name, dept_id, now),
            )
            exec_ids.append(cur.lastrowid)

        # Задачи + связи + статусы
        for topic, ticket, priority, state, due_offset, exec_idxs, statuses in ITEMS:
            due = (today + timedelta(days=due_offset)).isoformat()
            cur = conn.execute(
                """INSERT INTO items (topic, ticket, priority, state, due_date, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (topic, ticket, priority, state, due, now),
            )
            item_id = cur.lastrowid

            # M2M связи с исполнителями
            for idx in exec_idxs:
                conn.execute(
                    "INSERT OR IGNORE INTO item_executors (item_id, executor_id) VALUES (?, ?)",
                    (item_id, exec_ids[idx]),
                )

            # История статусов
            for status_offset, note in statuses:
                sdate = (today + timedelta(days=status_offset)).isoformat()
                conn.execute(
                    "INSERT INTO statuses (item_id, status_date, status_note, created_at) VALUES (?, ?, ?, ?)",
                    (item_id, sdate, note, now),
                )

        conn.commit()

        # Сводка
        counts = {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("departments", "executors", "items", "statuses", "item_executors")
        }
        print("Тестовые данные созданы:")
        for table, count in counts.items():
            print(f"  {table}: {count}")

    except Exception as e:
        conn.rollback()
        print(f"ОШИБКА: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
