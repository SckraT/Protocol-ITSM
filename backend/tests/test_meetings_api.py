"""Тесты API для совещаний."""
import pytest


@pytest.mark.asyncio
async def test_list_meetings_empty(client):
    """Пустой список совещаний при чистой БД."""
    response = await client.get("/api/meetings")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_meeting(client):
    """Создание совещания с минимальным набором полей."""
    response = await client.post(
        "/api/meetings",
        json={"title": "Планирование спринта"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Планирование спринта"
    assert data["participants"] == []
    assert data["item_count"] == 0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_meeting_with_date_and_description(client):
    """Создание совещания с датой и описанием."""
    response = await client.post(
        "/api/meetings",
        json={
            "title": "Ретро",
            "meeting_date": "2026-06-05",
            "description": "Обсуждение итогов",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["meeting_date"] == "2026-06-05"
    assert data["description"] == "Обсуждение итогов"


@pytest.mark.asyncio
async def test_create_meeting_with_participants(client):
    """Создание совещания с участниками (исполнителями)."""
    exec_r = await client.post("/api/executors", json={"name": "Иванов"})
    exec_id = exec_r.json()["id"]

    response = await client.post(
        "/api/meetings",
        json={"title": "С митинг", "participant_ids": [exec_id]},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["participants"]) == 1
    assert data["participants"][0]["name"] == "Иванов"


@pytest.mark.asyncio
async def test_create_meeting_empty_title_validation(client):
    """422 при пустом title (min_length=1)."""
    response = await client.post("/api/meetings", json={"title": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_meeting(client):
    """Получение совещания по ID."""
    r = await client.post("/api/meetings", json={"title": "Для получения"})
    meeting_id = r.json()["id"]

    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["id"] == meeting_id


@pytest.mark.asyncio
async def test_get_meeting_not_found(client):
    """404 для несуществующего совещания."""
    response = await client.get("/api/meetings/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_meeting(client):
    """Частичное обновление совещания (PATCH)."""
    r = await client.post("/api/meetings", json={"title": "Старое название"})
    meeting_id = r.json()["id"]

    response = await client.patch(
        f"/api/meetings/{meeting_id}",
        json={"title": "Новое название", "description": "Описание"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новое название"
    assert data["description"] == "Описание"


@pytest.mark.asyncio
async def test_update_meeting_not_found(client):
    """404 при обновлении несуществующего совещания."""
    response = await client.patch("/api/meetings/999", json={"title": "X"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_meeting(client):
    """Удаление совещания."""
    r = await client.post("/api/meetings", json={"title": "На удаление"})
    meeting_id = r.json()["id"]

    response = await client.delete(f"/api/meetings/{meeting_id}")
    assert response.status_code == 204

    get_response = await client.get(f"/api/meetings/{meeting_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_meeting_not_found(client):
    """404 при удалении несуществующего совещания."""
    response = await client.delete("/api/meetings/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_meetings_require_auth(anon_client):
    """401 без токена."""
    response = await anon_client.get("/api/meetings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_viewer_cannot_create(viewer_client):
    """403 для viewer при попытке создать совещание."""
    response = await viewer_client.post("/api/meetings", json={"title": "X"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_update(viewer_client, client):
    """403 для viewer при попытке обновить совещание."""
    r = await client.post("/api/meetings", json={"title": "Title"})
    meeting_id = r.json()["id"]

    response = await viewer_client.patch(
        f"/api/meetings/{meeting_id}", json={"title": "Новое"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_editor_can_create(editor_client):
    """201 для editor при создании совещания."""
    response = await editor_client.post("/api/meetings", json={"title": "From editor"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_meetings_search(client):
    """Поиск совещаний по title."""
    await client.post("/api/meetings", json={"title": "Планирование спринта"})
    await client.post("/api/meetings", json={"title": "Ретро команды"})

    response = await client.get("/api/meetings?search=спринт")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Планирование спринта"
