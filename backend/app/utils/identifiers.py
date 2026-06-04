"""
Нормализация и определение типа идентификатора входа.
Логин принимает username, email или телефон — тип определяется автоматически.
"""


def normalize_phone(raw: str) -> str:
    """Оставить только цифры, привести 8XXX → 7XXX (РФ-формат)."""
    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) == 11 and digits[0] == "8":
        digits = "7" + digits[1:]
    return digits


def detect_identifier(value: str) -> tuple[str, str]:
    """
    Определить тип идентификатора и вернуть нормализованное значение.
    Возвращает кортеж (kind, normalized): kind ∈ {"email", "phone", "username"}.
    """
    v = value.strip()
    if "@" in v:
        return "email", v.lower()
    # Телефон: достаточно цифр и только допустимые для номера символы
    if sum(c.isdigit() for c in v) >= 5 and all(c.isdigit() or c in "+()- " for c in v):
        return "phone", normalize_phone(v)
    return "username", v.lower()
