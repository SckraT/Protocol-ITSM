"""
JWT-безопасность: создание/верификация токенов, хэширование паролей.
Использует python-jose (JWT) и bcrypt напрямую (без passlib — несовместим с bcrypt>=4).
"""
from datetime import datetime, timedelta

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


# ── Пароли ──────────────────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Хэшировать пароль через bcrypt."""
    hashed = _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Проверить пароль против bcrypt-хэша."""
    return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT ─────────────────────────────────────────────────────────────────────


def _create_token(data: dict, expires_delta: timedelta) -> str:
    """Создать JWT-токен с заданным сроком жизни."""
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(username: str, role: str) -> str:
    """Создать короткоживущий access-токен (30 мин по умолчанию)."""
    return _create_token(
        {"sub": username, "role": role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(username: str) -> str:
    """Создать долгоживущий refresh-токен (7 дней по умолчанию)."""
    return _create_token(
        {"sub": username, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> dict | None:
    """
    Декодировать и верифицировать access-токен.
    Возвращает payload или None при ошибке.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> str | None:
    """
    Декодировать refresh-токен.
    Возвращает username или None при ошибке.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
