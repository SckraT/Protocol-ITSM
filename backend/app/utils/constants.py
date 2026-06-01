"""Константы приложения."""

# Поля CSV-экспорта
CSV_FIELDS = [
    "id",
    "topic",
    "ticket",
    "priority",
    "state",
    "due_date",
    "executors",
    "last_status_date",
    "last_status_note",
]

# Русские названия состояний
STATE_LABEL_RU = {
    "in_progress": "В работе",
    "postponed": "Отложено",
    "closed": "Закрыто",
}

# Русские названия приоритетов
PRIORITY_LABEL_RU = {
    "high": "Высокий",
    "medium": "Средний",
    "low": "Низкий",
    "": "",
}

# Цвета заливки для XLSX (hex без #)
PRIORITY_FILL_COLOR = {
    "high": "FEE2E2",
    "medium": "FEF9C3",
    "low": "DCFCE7",
}
STATE_FILL_COLOR = {
    "in_progress": "DBEAFE",
    "postponed": "F3F4F6",
    "closed": "D1FAE5",
}
