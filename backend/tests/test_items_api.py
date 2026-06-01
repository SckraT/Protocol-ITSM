"""Тесты API для задач протокола."""
import pytest


@pytest.mark.asyncio
async def test_list_items_empty(client):
    """Пустой список задач при чистой БД."""
    response = await client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_item(client):
    """Создание задачи."""
    response = await client.post("/api/items", json={
        "topic": "Тестовая задача",
        "state": "in_progress",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Тестовая задача"
    assert data["state"] == "in_progress"
    assert data["executors"] == []
    assert data["recent_statuses"] == []
    assert data["status_count"] == 0


@pytest.mark.asyncio
async def test_create_item_with_status(client):
    """Создание задачи с начальным статусом."""
    response = await client.post("/api/items", json={
        "topic": "Задача со статусом",
        "status_note": "Начальный статус",
        "status_date": "2026-06-01",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status_count"] == 1
    assert data["recent_statuses"][0]["status_note"] == "Начальный статус"


@pytest.mark.asyncio
async def test_get_item(client):
    """Получение задачи по ID."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


@pytest.mark.asyncio
async def test_get_item_not_found(client):
    """404 для несуществующей задачи."""
    response = await client.get("/api/items/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(client):
    """Частичное обновление задачи."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await client.patch(f"/api/items/{item_id}", json={"state": "closed"})
    assert response.status_code == 200
    assert response.json()["state"] == "closed"


@pytest.mark.asyncio
async def test_delete_item(client):
    """Удаление задачи."""
    r = await client.post("/api/items", json={"topic": "Задача"})
    item_id = r.json()["id"]

    response = await client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    get_response = await client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_state(client):
    """Фильтрация задач по состоянию."""
    await client.post("/api/items", json={"topic": "В работе", "state": "in_progress"})
    await client.post("/api/items", json={"topic": "Закрыта", "state": "closed"})

    response = await client.get("/api/items?state=closed")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["state"] == "closed"


@pytest.mark.asyncio
async def test_create_item_with_executors(client):
    """Создание задачи с исполнителями."""
    # Создаём исполнителя
    exec_r = await client.post("/api/executors", json={"name": "Иванов"})
    exec_id = exec_r.json()["id"]

    # Создаём задачу с исполнителем
    response = await client.post("/api/items", json={
        "topic": "Задача с исполнителем",
        "executor_ids": [exec_id],
    })
    assert response.status_code == 201
    data = response.json()
    assert len(data["executors"]) == 1
    assert data["executors"][0]["name"] == "Иванов"


@pytest.mark.asyncio
async def test_health_check(client):
    """Проверка health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
