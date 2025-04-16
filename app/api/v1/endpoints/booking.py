from typing import Optional
from app.models.booking import Booking
from app.schemas.booking import AvailableAccommodationSchema, BookingCreateSchema, BookingResponseSchema
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Query
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

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/", response_model=list[BookingResponseSchema])
async def get_bookings(
    target_date: Optional[date] = Query(None, description="Фильтрация по дате заезда"),
    limit: int = Query(10, ge=1, le=100, description="Сколько записей вернуть"),
    offset: int = Query(0, ge=0, description="Сколько записей пропустить"),
    db: AsyncSession = Depends(get_async_db)
):
    query = select(Booking).options(selectinload(Booking.accommodation))

    if target_date:
        query = query.where(
            or_(
                and_(
                    Booking.check_in_date <= target_date,
                    Booking.check_out_date > target_date
                ),
                and_(
                    Booking.check_in_date == target_date,
                    Booking.check_out_date == target_date
                )
            )
        )

    query = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    bookings = result.scalars().all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponseSchema)
async def get_booking_by_id(
    booking_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.accommodation))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    return booking

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreateSchema,
    db: Session = Depends(get_async_db)
):
    """
    При отправке POST запроса с нужными полями происходит поиск нужного
    размещения, подсчет цены, и создается бронь.
    Фронт нам должен отправить все данные исходя из предыдущего /find запроса
    Мы проверяем цену, если совпадает, то все ок
    """

    # Валидация входных данных
    if booking_data.check_in_date > booking_data.check_out_date:
        raise HTTPException(
            status_code=400,
            detail="Дата выезда должна быть не раньше даты заезда"
        )
    if booking_data.check_in_date < datetime.now().date():
        raise HTTPException(
            status_code=400,
            detail="Дата заезда не может быть в прошлом"
        )
    accommodation = db.query(Accommodation).get(booking_data.accommodation_id)

    if not accommodation:
        raise HTTPException(status_code=404, detail="Произошла ошибка")

    is_available = check_accommodation_availability(
        db,
        booking_data.accommodation_id,
        booking_data.check_in_date,
        booking_data.check_out_date
    )

    if not is_available:
        raise HTTPException(status_code=400, detail="Уже забронировано")

    price_info = calculate_accommodation_price(
        booking_data.accommodation_id,
        booking_data.check_in_date,
        booking_data.check_out_date,
        booking_data.guests
    )

    total_price = price_info["total"]

    if total_price == booking_data.total_price:
        try:
            booking = Booking(**booking_data.dict())
            db.add(booking)
            await db.flush()
            await db.commit()
            await db.refresh(booking)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Ошибка базы данных")

        return {"id": booking.id, "message": "Бронирование успешно создано"}

    else:
        raise HTTPException(status_code=400, detail="Произошла ошибка в цене")