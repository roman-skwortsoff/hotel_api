from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.session import get_async_db
from app.models.accommodation import Accommodation, AccommodationPrice
from app.schemas.accommodation import AccommodationSchema, AccommodationCreateSchema
from app.schemas.booking import AvailableAccommodationSchema
from app.utils.enums import AccommodationType, Weekday
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.services.booking_service import check_accommodation_availability, calculate_accommodation_price
from sqlalchemy import and_, or_
from datetime import date, datetime
from sqlalchemy.orm import Session


router = APIRouter(prefix="/accommodations", tags=["Accommodations"])

@router.get("/", response_model=list[AccommodationSchema])
async def get_accommodations(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Accommodation).options(selectinload(Accommodation.prices)))
    return result.scalars().all()

@router.get("/{accommodation_id}", response_model=AccommodationSchema)
async def get_accommodation_by_id(
    accommodation_id: int,
    db: AsyncSession = Depends(get_async_db) ):
    result = await db.execute(
        select(Accommodation)
        .options(selectinload(Accommodation.prices))
        .where(Accommodation.id == accommodation_id)
    )
    accommodation = result.scalar_one_or_none()

    if accommodation is None:
        raise HTTPException(status_code=404, detail="Accommodation not found")

    return accommodation

@router.post("/", response_model=AccommodationSchema)
async def create_accommodation(
    accommodation_data: AccommodationCreateSchema,
    db: AsyncSession = Depends(get_async_db)
):
    # Валидация типа размещения
    try:
        accommodation_type = AccommodationType(accommodation_data.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid accommodation type")

    # Создание объекта
    new_accommodation = Accommodation(
        name=accommodation_data.name,
        type=accommodation_type,
        short_description=accommodation_data.short_description,
        full_description=accommodation_data.full_description,
        image=accommodation_data.image,
        capacity=accommodation_data.capacity,
        count=accommodation_data.count,
        check_in_time=accommodation_data.check_in_time,
        check_out_time=accommodation_data.check_out_time,
        extra_beds_available=accommodation_data.extra_beds_available,
    )

    # Сохранение с обработкой цен
    try:
        db.add(new_accommodation)
        await db.flush()
        print("Записали в базу банных - ", new_accommodation)

        if accommodation_data.prices:
            for price in accommodation_data.prices:
                db.add(AccommodationPrice(
                    accommodation_id=new_accommodation.id,
                    weekday_type=Weekday(price.weekday_type),
                    price=price.price,
                    extra_bed_price=price.extra_bed_price
                ))
                print( "Записываем цену: ", new_accommodation.id, Weekday(price.weekday_type), price.price, price.extra_bed_price)


        await db.commit()
        await db.refresh(new_accommodation)

        return new_accommodation

    except Exception:
        await db.rollback()
        raise


@router.get("/find", response_model=list[AvailableAccommodationSchema])
async def get_available_accommodations(
        check_in_date: date = Query(..., description="Дата заезда"),
        check_out_date: date = Query(..., description="Дата выезда"),
        guests: int = Query(..., ge=1, description="Количество гостей"),
        db: Session = Depends(get_async_db),
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
