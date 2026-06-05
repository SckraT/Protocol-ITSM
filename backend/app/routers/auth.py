"""
Роутер аутентификации: login, refresh, me.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    TokenResponse,
)
from app.services.audit_service import log_event
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/login", response_model=TokenResponse, summary="Вход в систему")
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Аутентификация по логину/email/телефону и паролю. Возвращает access и refresh токены."""
    service = AuthService(db)
    result = await service.authenticate(body.identifier, body.password)
    if not result:
        await log_event(db, "login_failed", request=request, username=body.identifier)
        # Фиксируем аудит до raise: иначе rollback в get_db (из-за 401) удалит запись.
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await log_event(db, "login_success", request=request, username=result.username)
    return result


@router.post("/refresh", response_model=TokenResponse, summary="Обновить токен")
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
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
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    """Вернуть данные о текущем авторизованном пользователе."""
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        display_name=current_user.display_name,
        must_change_password=current_user.must_change_password,
    )


@router.post("/change-password", summary="Сменить свой пароль")
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Сменить пароль текущего пользователя (нужен старый пароль). Снимает флаг must_change_password."""
    service = AuthService(db)
    try:
        await service.change_password(current_user, body.old_password, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    await log_event(db, "password_change", request=request, username=current_user.username)
    return {"status": "ok"}
