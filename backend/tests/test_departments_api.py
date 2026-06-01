"""Тесты API для справочника отделов."""
import pytest


@pytest.mark.asyncio
async def test_list_departments_empty(client):
    """Пустой список отделов при чистой БД."""
    response = await client.get("/api/departments")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_department(client):
    """Создание отдела."""
    response = await client.post("/api/departments", json={"name": "ИТ"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ИТ"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_department_duplicate(client):
    """409 при попытке создать отдел с существующим именем."""
    await client.post("/api/departments", json={"name": "ИТ"})
    response = await client.post("/api/departments", json={"name": "ИТ"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_department(client):
    """Переименование отдела."""
    r = await client.post("/api/departments", json={"name": "ИТ"})
    dept_id = r.json()["id"]

    response = await client.put(f"/api/departments/{dept_id}", json={"name": "ИТ отдел"})
    assert response.status_code == 200
    assert response.json()["name"] == "ИТ отдел"


@pytest.mark.asyncio
async def test_update_department_not_found(client):
    """404 при обновлении несуществующего отдела."""
    response = await client.put("/api/departments/999", json={"name": "Новый"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_department(client):
    """Удаление отдела."""
    r = await client.post("/api/departments", json={"name": "ИТ"})
    dept_id = r.json()["id"]

    response = await client.delete(f"/api/departments/{dept_id}")
    assert response.status_code == 204

    # Проверяем, что удалён
    list_response = await client.get("/api/departments")
    assert all(d["id"] != dept_id for d in list_response.json())


@pytest.mark.asyncio
async def test_delete_department_not_found(client):
    """404 при удалении несуществующего отдела."""
    response = await client.delete("/api/departments/999")
    assert response.status_code == 404
