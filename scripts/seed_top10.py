"""
Добавляет 10 оставшихся задач к уже существующим демо-данным.
Требует запущенного стека (порт 8000).
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

BASE_URL = "http://protocol-protocol-1:8000/api"
ADMIN_CREDENTIALS = {"identifier": "admin", "password": "ScR_1630!"}

TODAY = date.today()

def d(offset: int) -> str:
    return (TODAY + timedelta(days=offset)).isoformat()

def api(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict | list:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {path} → {exc.code}: {exc.read().decode()}") from exc

def post(path: str, body: dict, token: str) -> dict:
    return api("POST", path, body, token)  # type: ignore[return-value]

def get_list(path: str, token: str) -> list:
    return api("GET", path, token=token)  # type: ignore[return-value]

def main() -> None:
    # 1. Логин
    tokens = post("/auth/login", ADMIN_CREDENTIALS, "")
    token: str = tokens["access_token"]  # type: ignore[index]
    print("✓ авторизован")

    # 2. Загрузить существующие сущности
    depts  = {d["name"]: d["id"] for d in get_list("/departments", token)}
    execs  = {e["name"]: e["id"] for e in get_list("/executors",   token)}
    meet_resp = api("GET", "/meetings?page_size=100", token=token)
    meetings = {m["title"]: m["id"] for m in meet_resp["items"]}  # type: ignore[index]

    print(f"  Найдено: {len(depts)} отделов, {len(execs)} исполнителей, {len(meetings)} совещаний")

    # Короткие алиасы для удобства
    def eid(name: str) -> int:
        return execs[name]

    mid = lambda title: meetings[title]

    # 3. 10 новых задач
    new_items = [
        {
            "topic": "Тюнинг PostgreSQL (shared_buffers, work_mem)",
            "ticket": "INF-103", "priority": "medium", "state": "in_progress",
            "due_date": d(12), "executor_ids": [eid("Иванов Андрей Сергеевич"), eid("Петров Владимир Николаевич")],
            "meeting_id": mid("Ревью инфраструктуры"),
            "status_date": d(-3), "status_note": "Собрана статистика pg_stat",
        },
        {
            "topic": "Настройка log rotation для всех сервисов",
            "ticket": "INF-104", "priority": "low", "state": "in_progress",
            "due_date": d(35), "executor_ids": [eid("Соколова Мария Ивановна")],
        },
        {
            "topic": "Подготовка стенда нагрузочного тестирования",
            "ticket": "DEV-102", "priority": "high", "state": "in_progress",
            "due_date": d(8),
            "executor_ids": [eid("Морозов Алексей Викторович"), eid("Волков Игорь Олегович")],
            "meeting_id": mid("Архитектурный совет"),
            "status_date": d(-2), "status_note": "Развёрнут k6",
        },
        {
            "topic": "Переход API на версионирование /v2",
            "ticket": "DEV-103", "priority": "medium", "state": "postponed",
            "due_date": d(60),
            "executor_ids": [eid("Волков Игорь Олегович"), eid("Попов Сергей Андреевич")],
            "meeting_id": mid("Архитектурный совет"),
            "status_date": d(-10), "status_note": "RFC передан на согласование",
        },
        {
            "topic": "Автоочистка устаревших сессий",
            "ticket": "DEV-104", "priority": "low", "state": "in_progress",
            "due_date": d(45), "executor_ids": [eid("Захарова Татьяна Григорьевна")],
        },
        {
            "topic": "SLA Dashboard для менеджмента",
            "ticket": "ANA-101", "priority": "medium", "state": "in_progress",
            "due_date": d(18),
            "executor_ids": [eid("Андреев Максим Дмитриевич"), eid("Виноградов Борис Николаевич")],
            "meeting_id": mid("Итоги полугодия"),
            "status_date": d(-4), "status_note": "Показатели согласованы с руководством",
        },
        {
            "topic": "Оценка перехода на PostgreSQL 17",
            "ticket": "INF-105", "priority": "low", "state": "postponed",
            "due_date": d(90),
            "executor_ids": [eid("Иванов Андрей Сергеевич"), eid("Петров Владимир Николаевич")],
            "status_date": d(-5), "status_note": "Ожидаем GA-релиза",
        },
        {
            "topic": "Ревью зависимостей: npm audit",
            "ticket": "DEV-105", "priority": "medium", "state": "closed",
            "due_date": d(-3),
            "executor_ids": [eid("Лебедева Наталья Михайловна"), eid("Захарова Татьяна Григорьевна")],
            "meeting_id": mid("Sprint review — июнь"),
            "status_date": d(-5), "status_note": "Найдено 4 уязвимости",
        },
        {
            "topic": "Обновление схем Kafka-топиков",
            "ticket": "DEV-106", "priority": "high", "state": "in_progress",
            "due_date": d(6),
            "executor_ids": [eid("Морозов Алексей Викторович"), eid("Волков Игорь Олегович")],
            "meeting_id": mid("Архитектурный совет"),
            "status_date": d(-1), "status_note": "Новая схема протестирована на стенде",
        },
        {
            "topic": "Профилирование памяти Python-сервиса",
            "ticket": "DEV-107", "priority": "high", "state": "in_progress",
            "due_date": d(4), "executor_ids": [eid("Волков Игорь Олегович")],
            "status_date": d(-2), "status_note": "Запущен memory_profiler — утечка найдена",
        },
    ]

    ok, fail = 0, 0
    for item in new_items:
        try:
            # Вытащить доп. статус если нужен (у DEV-105: 2 статуса)
            extra_statuses: list[tuple[int, str]] = []
            if item.get("ticket") == "DEV-105":
                extra_statuses = [(-3, "Все уязвимости обновлены")]

            result = post("/items", item, token)
            for offset, note in extra_statuses:
                post(f"/items/{result['id']}/statuses", {
                    "status_date": d(offset), "status_note": note,
                }, token)
            ok += 1
            print(f"  ✓ [{item['ticket']}] {item['topic']}")
        except RuntimeError as exc:
            fail += 1
            print(f"  ✗ [{item['ticket']}] {exc}")

    print(f"\nДобавлено: {ok}, ошибок: {fail}")
    if fail:
        sys.exit(1)

if __name__ == "__main__":
    main()
