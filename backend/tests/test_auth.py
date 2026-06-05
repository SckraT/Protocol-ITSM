"""Тесты аутентификации: вход по разным идентификаторам, refresh, неактивный юзер."""
import pytest

from app.models.user import RoleEnum
from tests.conftest import TEST_PASSWORD, _seed_user


@pytest.mark.asyncio
async def test_login_by_username(anon_client, db_session):
    """Вход по username."""
    await _seed_user(db_session, "ivanov", RoleEnum.editor)
    r = await anon_client.post("/api/auth/login", json={"identifier": "ivanov", "password": TEST_PASSWORD})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "ivanov"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_by_email(anon_client, db_session):
    """Вход по email (регистронезависимо)."""
    await _seed_user(db_session, "petrov", RoleEnum.editor, email="petrov@mail.ru")
    r = await anon_client.post("/api/auth/login", json={"identifier": "Petrov@MAIL.ru", "password": TEST_PASSWORD})
    assert r.status_code == 200
    assert r.json()["username"] == "petrov"


@pytest.mark.asyncio
async def test_login_by_phone(anon_client, db_session):
    """Вход по телефону в произвольном формате."""
    await _seed_user(db_session, "sidorov", RoleEnum.editor, phone="79991234567")
    r = await anon_client.post("/api/auth/login", json={"identifier": "+7 (999) 123-45-67", "password": TEST_PASSWORD})
    assert r.status_code == 200
    assert r.json()["username"] == "sidorov"


@pytest.mark.asyncio
async def test_login_wrong_password(anon_client, db_session):
    """Неверный пароль → 401."""
    await _seed_user(db_session, "user1", RoleEnum.viewer)
    r = await anon_client.post("/api/auth/login", json={"identifier": "user1", "password": "wrongpass"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(anon_client, db_session):
    """Заблокированный пользователь не может войти → 401."""
    user = await _seed_user(db_session, "blocked", RoleEnum.viewer)
    user.is_active = False
    await db_session.flush()
    r = await anon_client.post("/api/auth/login", json={"identifier": "blocked", "password": TEST_PASSWORD})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(anon_client, db_session):
    """Refresh выдаёт новую пару токенов."""
    await _seed_user(db_session, "refresher", RoleEnum.editor)
    login = await anon_client.post("/api/auth/login", json={"identifier": "refresher", "password": TEST_PASSWORD})
    refresh_token = login.json()["refresh_token"]

    r = await anon_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert r.json()["access_token"]


@pytest.mark.asyncio
async def test_must_change_password_flag_in_login(anon_client, db_session):
    """Флаг must_change_password отдаётся в ответе login."""
    await _seed_user(db_session, "pending", RoleEnum.viewer, must_change_password=True)
    r = await anon_client.post("/api/auth/login", json={"identifier": "pending", "password": TEST_PASSWORD})
    assert r.status_code == 200
    assert r.json()["must_change_password"] is True


@pytest.mark.asyncio
async def test_audit_log_records_login_events(anon_client, db_session):
    """Успешный и неуспешный вход фиксируются в аудит-логе."""
    from sqlalchemy import select

    from app.models.audit_log import AuditLog

    await _seed_user(db_session, "audituser", RoleEnum.editor)
    await anon_client.post("/api/auth/login", json={"identifier": "audituser", "password": "wrongpass"})
    await anon_client.post("/api/auth/login", json={"identifier": "audituser", "password": TEST_PASSWORD})

    rows = (await db_session.execute(select(AuditLog))).scalars().all()
    events = {r.event_type for r in rows}
    assert "login_failed" in events
    assert "login_success" in events
