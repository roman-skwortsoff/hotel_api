from select import select
from app.models.accommodation import Accommodation
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession



@pytest.mark.asyncio
async def test_get_accommodations(async_client):
    response = await async_client.get("/accommodations/")
    print('!!!!!!!!!! ТЕСТ ПРОЙДЕН !!!!!!!!!!')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_accommodation(async_client: AsyncClient):
    test_data = {
        "name": "Тестовый дом",
        "type": "guest_house",
        "short_description": "Краткое описание",
        "full_description": "Полное описание",
        "image": "https://example.com/image.jpg",
        "capacity": 4,
        "count": 1,
        "check_in_time": "15:00",
        "check_out_time": "12:00",
        "extra_beds_available": 1,
        "prices": [
            {"weekday_type": "weekday", "price": 100.0, "extra_bed_price": 20.0},
            {"weekday_type": "weekend", "price": 150.0, "extra_bed_price": 25.0}
        ]
    }

    # Для отладки
    print("\nОтправляемые данные в тесте:", test_data)

    response = await async_client.post("/accommodations/", json=test_data)

    if response.status_code == 422:
        print("Детали ошибки:", response.json())

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Тестовый дом"