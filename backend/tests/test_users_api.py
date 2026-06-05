"""Тесты API для управления пользователями (admin-only)."""
import pytest
from sqlalchemy import select

from app.models.user import RoleEnum, User
from tests.conftest import TEST_PASSWORD, _seed_user


async def _get_admin_id(client) -> int:
    """Получить id текущего admin через /api/users (ищем по username admin_t)."""
    response = await client.get("/api/users")
    assert response.status_code == 200
    users = response.json()
    admin = next(u for u in users if u["username"] == "admin_t")
    return admin["id"]


@pytest.mark.asyncio
async def test_list_users_admin(client):
    """GET /api/users возвращает список пользователей для admin."""
    response = await client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["username"] == "admin_t"
    assert data[0]["role"] == "admin"
    assert data[0]["is_active"] is True


@pytest.mark.asyncio
async def test_list_users_editor_forbidden(editor_client):
    """403 для editor при попытке получить список пользователей."""
    response = await editor_client.get("/api/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_viewer_forbidden(viewer_client):
    """403 для viewer при попытке получить список пользователей."""
    response = await viewer_client.get("/api/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_unauth(anon_client):
    """401 без токена."""
    response = await anon_client.get("/api/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user(client):
    """Создание нового пользователя."""
    response = await client.post(
        "/api/users",
        json={
            "username": "new_user",
            "password": TEST_PASSWORD,
            "role": "editor",
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "Иванович",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_user"
    assert data["role"] == "editor"
    assert data["last_name"] == "Иванов"
    assert data["display_name"] == "Иванов И.И."


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client):
    """409 при попытке создать пользователя с занятым username."""
    response = await client.post(
        "/api/users",
        json={
            "username": "admin_t",
            "password": TEST_PASSWORD,
            "last_name": "Дубль",
            "first_name": "Дубль",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_user_short_username(client):
    """422 при username короче 3 символов."""
    response = await client.post(
        "/api/users",
        json={
            "username": "ab",
            "password": TEST_PASSWORD,
            "last_name": "А",
            "first_name": "Б",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_short_password(client):
    """422 при пароле короче 8 символов."""
    response = await client.post(
        "/api/users",
        json={
            "username": "valid_name",
            "password": "short",
            "last_name": "Фамилия",
            "first_name": "Имя",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, db_session):
    """409 при попытке создать пользователя с занятым email."""
    await _seed_user(db_session, "first", RoleEnum.viewer, email="a@b.c")
    await db_session.flush()

    response = await client.post(
        "/api/users",
        json={
            "username": "second",
            "password": TEST_PASSWORD,
            "email": "a@b.c",
            "last_name": "Ф",
            "first_name": "И",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_user_missing_last_name(client):
    """422 при пустой фамилии (обязательное поле)."""
    response = await client.post(
        "/api/users",
        json={
            "username": "noname",
            "password": TEST_PASSWORD,
            "last_name": "",
            "first_name": "Имя",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_role(client, db_session):
    """PATCH: смена роли пользователя с viewer на editor."""
    target = await _seed_user(db_session, "viewer_user", RoleEnum.viewer)
    await db_session.flush()

    response = await client.patch(
        f"/api/users/{target.id}",
        json={"role": "editor"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "editor"


@pytest.mark.asyncio
async def test_update_user_deactivate(client, db_session):
    """PATCH: деактивация пользователя (is_active=false)."""
    target = await _seed_user(db_session, "to_deactivate", RoleEnum.editor)
    await db_session.flush()

    response = await client.patch(
        f"/api/users/{target.id}",
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_user_not_found(client):
    """404 при PATCH несуществующего пользователя."""
    response = await client.patch("/api/users/999", json={"role": "viewer"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_self_role_forbidden(client):
    """400: admin не может изменить роль самому себе."""
    admin_id = await _get_admin_id(client)

    response = await client.patch(
        f"/api/users/{admin_id}",
        json={"role": "viewer"},
    )
    assert response.status_code == 400
    assert "роль" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_self_deactivate_forbidden(client):
    """400: admin не может деактивировать собственный аккаунт."""
    admin_id = await _get_admin_id(client)

    response = await client.patch(
        f"/api/users/{admin_id}",
        json={"is_active": False},
    )
    assert response.status_code == 400
    assert "заблокировать" in response.json()["detail"].lower() or "аккаунт" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_self_password_allowed(client, db_session):
    """Self-PATCH пароля разрешён (не попадает под self-protection от роли/is_active)."""
    admin_id = await _get_admin_id(client)

    response = await client.patch(
        f"/api/users/{admin_id}",
        json={"password": "NewStrongPass1"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_user(client, db_session):
    """DELETE: удаление существующего пользователя."""
    target = await _seed_user(db_session, "to_delete", RoleEnum.viewer)
    await db_session.flush()

    response = await client.delete(f"/api/users/{target.id}")
    assert response.status_code == 204

    # Проверяем, что удалён
    get_response = await client.get("/api/users")
    assert all(u["id"] != target.id for u in get_response.json())


@pytest.mark.asyncio
async def test_delete_user_not_found(client):
    """404 при удалении несуществующего пользователя."""
    response = await client.delete("/api/users/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_self_forbidden(client):
    """400: admin не может удалить собственный аккаунт."""
    admin_id = await _get_admin_id(client)

    response = await client.delete(f"/api/users/{admin_id}")
    assert response.status_code == 400
    assert "собственный" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_role_writes_audit(client, db_session):
    """При смене роли создаётся запись в audit_log."""
    from app.models.audit_log import AuditLog

    target = await _seed_user(db_session, "audited_user", RoleEnum.viewer)
    await db_session.flush()

    response = await client.patch(
        f"/api/users/{target.id}",
        json={"role": "editor"},
    )
    assert response.status_code == 200

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.event_type == "role_change")
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    assert logs[0].payload["target"] == "audited_user"
    assert logs[0].payload["old_role"] == "viewer"
    assert logs[0].payload["new_role"] == "editor"


@pytest.mark.asyncio
async def test_create_user_with_executor_sync(client, db_session):
    """При создании пользователя с ФИО синхронизируется имя привязанного исполнителя."""
    from app.models.executor import Executor

    target = await _seed_user(db_session, "linked_user", RoleEnum.viewer)
    await db_session.flush()
    executor = Executor(
        name="Старое имя",
        user_id=target.id,
    )
    db_session.add(executor)
    await db_session.flush()

    response = await client.patch(
        f"/api/users/{target.id}",
        json={"last_name": "Новая", "first_name": "Фамилия"},
    )
    assert response.status_code == 200

    await db_session.refresh(executor)
    assert "Новая" in executor.name
