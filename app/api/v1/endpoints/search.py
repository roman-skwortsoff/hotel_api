from app.schemas.booking import AvailableAccommodationSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from app.db.session import get_async_db, get_db
from app.models.accommodation import Accommodation, AccommodationPrice
from app.schemas.accommodation import AccommodationSchema, AccommodationCreateSchema
from app.utils.enums import AccommodationType, Weekday
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func
from datetime import date, datetime, time
from app.services.booking_service import check_accommodation_availability, calculate_accommodation_price

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/find", response_model=list[AvailableAccommodationSchema])
async def search_accommodations(
        check_in_date: date,
        check_out_date: date,
        guests: int,
        db: Session = Depends(get_async_db)
):
    """
    Поиск доступных вариантов размещения.

    Параметры:
    - check_in_date: дата заезда
    - check_out_date: дата выезда
    - guests: количество гостей
    Возвращает список доступных вариантов с рассчитанными ценами.
    """

    # Валидация входных данных
    if check_in_date > check_out_date:
        raise HTTPException(
            status_code=400,
            detail="Дата выезда должна быть не раньше даты заезда"
        )
    if check_in_date < datetime.now().date():
        raise HTTPException(
            status_code=400,
            detail="Дата заезда не может быть в прошлом"
        )

    # Получаем все подходящие по вместимости варианты
    query = (db.query(Accommodation).
             filter(or_(
        Accommodation.capacity >= guests,   # Основная вместимость достаточна
        and_(Accommodation.capacity + Accommodation.extra_beds_available >= guests, Accommodation.extra_beds_available > 0) # Или есть доп. места
        )
    ))

    suitable_accommodations = query.all()
    available_accommodations = []

    # Проверяем каждый вариант на доступность
    for acc in suitable_accommodations:
        is_available = check_accommodation_availability(
            db, acc.id, check_in_date, check_out_date
        )

        if not is_available:
            continue  # Пропускаем занятые

        # Рассчитываем цену (вынесли в отдельную функцию)
        price_info = calculate_accommodation_price(
            acc, check_in_date, check_out_date, guests
        )

        available_accommodations.append({
            "accommodation": acc,
            "total_price": price_info["total"],
            "nights": price_info["nights"],
            "requires_extra_bed": guests > acc.capacity,
            "prices": price_info["details"]
        })

    return available_accommodations