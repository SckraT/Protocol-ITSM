"""Тесты API для справочника исполнителей."""
import pytest


@pytest.mark.asyncio
async def test_list_executors_empty(client):
    """Пустой список исполнителей при чистой БД."""
    response = await client.get("/api/executors")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_executor(client):
    """Создание исполнителя с минимальным набором полей."""
    response = await client.post("/api/executors", json={"name": "Иванов И.И."})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Иванов И.И."
    assert data["department_id"] is None
    assert data["department_name"] is None
    assert data["user_id"] is None
    assert data["user"] is None
    assert "id" in data


@pytest.mark.asyncio
async def test_create_executor_duplicate(client):
    """409 при попытке создать исполнителя с занятым именем."""
    await client.post("/api/executors", json={"name": "Петров"})
    response = await client.post("/api/executors", json={"name": "Петров"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_executor_empty_name_validation(client):
    """422 при пустом name (min_length=1)."""
    response = await client.post("/api/executors", json={"name": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_executor_with_department(client, db_session):
    """Создание исполнителя с привязкой к отделу — в ответе подтянется department_name."""
    from tests.conftest import _seed_department

    dept = await _seed_department(db_session, name="ИТ отдел")
    await db_session.flush()

    response = await client.post(
        "/api/executors",
        json={"name": "Сидоров", "department_id": dept.id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["department_id"] == dept.id
    assert data["department_name"] == "ИТ отдел"


@pytest.mark.asyncio
async def test_create_executor_with_invalid_department(client):
    """404 при указании несуществующего отдела."""
    response = await client.post(
        "/api/executors",
        json={"name": "Тест", "department_id": 999},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_executor(client, db_session):
    """Обновление имени и отдела исполнителя (PUT)."""
    from tests.conftest import _seed_department

    r = await client.post("/api/executors", json={"name": "Старое имя"})
    exec_id = r.json()["id"]
    new_dept = await _seed_department(db_session, name="Новый отдел")
    await db_session.flush()

    response = await client.put(
        f"/api/executors/{exec_id}",
        json={"name": "Новое имя", "department_id": new_dept.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Новое имя"
    assert data["department_id"] == new_dept.id


@pytest.mark.asyncio
async def test_update_executor_not_found(client):
    """404 при обновлении несуществующего исполнителя."""
    response = await client.put("/api/executors/999", json={"name": "X"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_executor(client):
    """Удаление исполнителя."""
    r = await client.post("/api/executors", json={"name": "На удаление"})
    exec_id = r.json()["id"]

    response = await client.delete(f"/api/executors/{exec_id}")
    assert response.status_code == 204

    list_response = await client.get("/api/executors")
    assert all(e["id"] != exec_id for e in list_response.json())


@pytest.mark.asyncio
async def test_delete_executor_not_found(client):
    """404 при удалении несуществующего исполнителя."""
    response = await client.delete("/api/executors/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_options_editor(editor_client, db_session):
    """GET /executors/user-options возвращает список УЗ для editor."""
    from app.models.user import RoleEnum
    from tests.conftest import _seed_user

    await _seed_user(db_session, "user_a", RoleEnum.viewer)
    await _seed_user(db_session, "user_b", RoleEnum.editor)
    await db_session.flush()

    response = await editor_client.get("/api/executors/user-options")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = {u["username"] for u in data}
    assert "user_a" in usernames
    assert "user_b" in usernames


@pytest.mark.asyncio
async def test_user_options_viewer_forbidden(viewer_client):
    """403 для viewer при попытке получить список УЗ."""
    response = await viewer_client.get("/api/executors/user-options")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_executors_require_auth(anon_client):
    """401 без токена."""
    response = await anon_client.get("/api/executors")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_viewer_cannot_create(viewer_client):
    """403 для viewer при попытке создать исполнителя."""
    response = await viewer_client.post("/api/executors", json={"name": "X"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_can_list(viewer_client):
    """200 для viewer при чтении списка исполнителей."""
    response = await viewer_client.get("/api/executors")
    assert response.status_code == 200
