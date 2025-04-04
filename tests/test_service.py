from select import select
from app.models.accommodation import Accommodation
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_services(async_client):
    response = await async_client.get("/services/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_services(async_client: AsyncClient):
    test_data = {
        "name": "Тестовый сервис",
        "short_description": "Краткое описание",
        "full_description": "Полное описание",
        "image": "https://example.com/image.jpg",
        "is_free": "True",
        "is_agreement_required": "False",
        "prices": [
            {"weekday_type": "weekday", "name": "базовый часовой", "duration_hours": 1, "price": 1000},
            {"weekday_type": "weekday", "name": "оптимальный", "duration_hours": 3, "price": 2000},
            {"weekday_type": "weekend", "name": "базовый часовой", "duration_hours": 1, "price": 2000}
        ]
    }

    # Для отладки
    print("\nОтправляемые данные в тесте:", test_data)

    response = await async_client.post("/services/", json=test_data)

    if response.status_code == 422:
        print("Детали ошибки:", response.json())

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Тестовый сервис"