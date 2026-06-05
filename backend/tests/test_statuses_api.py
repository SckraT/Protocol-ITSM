"""Тесты API для истории статусов задач."""
import pytest

from tests.conftest import _seed_item


@pytest.mark.asyncio
async def test_list_statuses_empty(client):
    """GET /items/{id}/statuses — пустой список для новой задачи."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await client.get(f"/api/items/{item_id}/statuses")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_statuses_item_not_found(client):
    """404 при запросе статусов несуществующей задачи."""
    response = await client.get("/api/items/999/statuses")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_status(client):
    """POST: добавление записи статуса к задаче."""
    r = await client.post("/api/items", json={"topic": "Задача со статусом"})
    item_id = r.json()["id"]

    response = await client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "Начата работа", "status_date": "2026-06-05"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["item_id"] == item_id
    assert data["status_note"] == "Начата работа"
    assert data["status_date"] == "2026-06-05"


@pytest.mark.asyncio
async def test_add_status_item_not_found(client):
    """404 при добавлении статуса к несуществующей задаче."""
    response = await client.post(
        "/api/items/999/statuses",
        json={"status_note": "X"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_status_viewer_forbidden(viewer_client, client):
    """403 для viewer при попытке добавить статус."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await viewer_client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "X"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_status(client):
    """DELETE: удаление записи статуса."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    s = await client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "На удаление"},
    )
    status_id = s.json()["id"]

    response = await client.delete(f"/api/statuses/{status_id}")
    assert response.status_code == 204

    list_response = await client.get(f"/api/items/{item_id}/statuses")
    assert all(s["id"] != status_id for s in list_response.json())


@pytest.mark.asyncio
async def test_delete_status_not_found(client):
    """404 при удалении несуществующего статуса."""
    response = await client.delete("/api/statuses/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_multiple_statuses_chronological(client):
    """Несколько статусов возвращаются в обратном хронологическом порядке."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    await client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "Первый", "status_date": "2026-06-01"},
    )
    await client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "Второй", "status_date": "2026-06-03"},
    )
    await client.post(
        f"/api/items/{item_id}/statuses",
        json={"status_note": "Третий", "status_date": "2026-06-05"},
    )

    response = await client.get(f"/api/items/{item_id}/statuses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Обратный хронологический порядок: самый поздний — первый
    assert data[0]["status_note"] == "Третий"
    assert data[1]["status_note"] == "Второй"
    assert data[2]["status_note"] == "Первый"


@pytest.mark.asyncio
async def test_status_history_via_item_create(client):
    """При создании задачи со status_note — начальный статус попадает в историю."""
    response = await client.post(
        "/api/items",
        json={
            "topic": "Задача",
            "status_note": "Начальный статус",
            "status_date": "2026-06-01",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status_count"] == 1
    assert data["recent_statuses"][0]["status_note"] == "Начальный статус"

    # Проверяем через /statuses endpoint
    list_response = await client.get(f"/api/items/{data['id']}/statuses")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_statuses_require_auth(anon_client, client):
    """401 без токена."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await anon_client.get(f"/api/items/{item_id}/statuses")
    assert response.status_code == 401
