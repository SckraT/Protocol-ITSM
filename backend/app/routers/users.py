"""
Роутер управления пользователями (только Admin).
CRUD операции: список, создание, обновление роли/статуса/пароля, удаление.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security import hash_password
from app.services.executor_service import sync_executor_name

# Весь роутер доступен только Admin — guard на уровне роутера.
router = APIRouter(prefix="/users", tags=["Пользователи"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserResponse], summary="Список пользователей")
async def list_users(db: AsyncSession = Depends(get_db)):
    """Вернуть всех пользователей. Только Admin."""
    repo = UserRepository(db)
    users = await repo.list(limit=1000)
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Создать пользователя")
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создать нового пользователя. Только Admin."""
    repo = UserRepository(db)

    # Проверка уникальности username
    existing = await repo.get_by_username(body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь '{body.username}' уже существует",
        )

    # Проверка уникальности email/телефона
    if body.email and await repo.get_by_email(body.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже используется")
    if body.phone and await repo.get_by_phone(body.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Телефон уже используется")

    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=True,
        email=body.email,
        phone=body.phone,
        last_name=body.last_name,
        first_name=body.first_name,
        middle_name=body.middle_name,
    )
    return await repo.create(user)


@router.patch("/{user_id}", response_model=UserResponse, summary="Обновить пользователя")
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Обновить роль, статус или пароль пользователя. Только Admin."""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Нельзя изменить роль или заблокировать себя
    if user_id == admin.id and (body.role is not None or body.is_active is False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить роль или заблокировать собственный аккаунт",
        )

    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password is not None:
        user.hashed_password = hash_password(body.password)

    # Email/телефон: проверка уникальности при изменении (None — снять)
    if "email" in body.model_fields_set:
        if body.email:
            other = await repo.get_by_email(body.email)
            if other and other.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже используется")
        user.email = body.email
    if "phone" in body.model_fields_set:
        if body.phone:
            other = await repo.get_by_phone(body.phone)
            if other and other.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Телефон уже используется")
        user.phone = body.phone

    # ФИО
    if "last_name" in body.model_fields_set and body.last_name is not None:
        user.last_name = body.last_name
    if "first_name" in body.model_fields_set and body.first_name is not None:
        user.first_name = body.first_name
    if "middle_name" in body.model_fields_set:
        user.middle_name = body.middle_name

    # Синхрон имени привязанного исполнителя из ФИО
    sync_executor_name(user)

    await repo.session.flush()
    await repo.session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить пользователя")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Удалить пользователя. Только Admin. Нельзя удалить себя."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить собственный аккаунт",
        )

    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    await repo.delete(user)
