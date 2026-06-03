"""
Роутер аутентификации: login, refresh, me.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/login", response_model=TokenResponse, summary="Вход в систему")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Аутентификация по логину и паролю. Возвращает access и refresh токены."""
    service = AuthService(db)
    result = await service.authenticate(body.username, body.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.post("/refresh", response_model=TokenResponse, summary="Обновить токен")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Получить новый access-токен по refresh-токену."""
    service = AuthService(db)
    result = await service.refresh(body.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh-токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.get("/me", response_model=MeResponse, summary="Текущий пользователь")
async def get_me(current_user: User = Depends(get_current_user)):
    """Вернуть данные о текущем авторизованном пользователе."""
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
    )
