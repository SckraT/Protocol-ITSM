"""
FastAPI-зависимости для авторизации.

Иерархия:
    get_current_user  — любой авторизованный (viewer, editor, admin)
    require_editor    — editor и admin
    require_admin     — только admin
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import RoleEnum, User
from app.repositories.user_repository import UserRepository
from app.security import decode_access_token

# Схема извлечения Bearer-токена из заголовка Authorization
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Зависимость: любой авторизованный пользователь (viewer+).
    Декодирует JWT, загружает User из БД. Выбрасывает 401 при ошибке.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub", "")
    repo = UserRepository(db)
    user = await repo.get_by_username(username)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или заблокирован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def forbid_pending_password_change(current_user: User = Depends(get_current_user)) -> User:
    """
    Зависимость: блокирует доступ ко всем защищённым ресурсам, пока пользователь
    не сменил обязательный пароль. Эндпоинты /auth/* (включая change-password) остаются
    доступны, т.к. на них этот guard не навешивается.
    """
    if current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"must_change_password": True, "message": "Требуется смена пароля"},
        )
    return current_user


async def require_editor(current_user: User = Depends(forbid_pending_password_change)) -> User:
    """Зависимость: editor или admin. Выбрасывает 403 для viewer."""
    if current_user.role == RoleEnum.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль editor или admin.",
        )
    return current_user


async def require_admin(current_user: User = Depends(forbid_pending_password_change)) -> User:
    """Зависимость: только admin. Выбрасывает 403 для viewer и editor."""
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль admin.",
        )
    return current_user
