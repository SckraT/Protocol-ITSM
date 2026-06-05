"""Тесты разграничения прав: viewer/editor/admin и guard смены пароля."""
import pytest

from app.models.user import RoleEnum
from app.security import create_access_token
from tests.conftest import _make_client, _seed_user


@pytest.mark.asyncio
async def test_anon_cannot_list_items(anon_client):
    """Без авторизации защищённый ресурс → 401."""
    r = await anon_client.get("/api/items")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_viewer_can_read_items(viewer_client):
    """Viewer может читать список задач."""
    r = await viewer_client.get("/api/items")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create_item(viewer_client):
    """Viewer не может создавать задачи → 403."""
    r = await viewer_client.post("/api/items", json={"topic": "Запрещено"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_editor_can_create_item(editor_client):
    """Editor может создавать задачи."""
    r = await editor_client.post("/api/items", json={"topic": "Разрешено"})
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_editor_cannot_manage_users(editor_client):
    """Editor не имеет доступа к управлению пользователями → 403."""
    r = await editor_client.get("/api/users")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_manage_users(client):
    """Admin имеет доступ к списку пользователей."""
    r = await client.get("/api/users")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_pending_password_change_blocks_access(db_session):
    """Пользователь с must_change_password не имеет доступа к ресурсам → 403."""
    await _seed_user(db_session, "pending_u", RoleEnum.editor, must_change_password=True)
    token = create_access_token("pending_u", RoleEnum.editor.value)
    async with _make_client(db_session, token) as c:
        r = await c.get("/api/items")
        assert r.status_code == 403
        detail = r.json()["detail"]
        assert detail.get("must_change_password") is True
        # change-password остаётся доступен
        r2 = await c.post(
            "/api/auth/change-password",
            json={"old_password": "password123", "new_password": "newpassword1"},
        )
        assert r2.status_code == 200
    from app.main import app
    app.dependency_overrides.clear()
