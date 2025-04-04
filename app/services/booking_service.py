from calendar import weekday
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.accommodation import Accommodation, AccommodationPrice
from app.models.booking import Booking
from app.utils.enums import AccommodationType, Weekday


def check_accommodation_availability(
        db: Session,
        accommodation_id: int,
        check_in_date: date,
        check_out_date: date
) -> bool:
    """
    Проверяет доступность конкретного размещения на даты.
    Для gazebo (check_in_date == check_out_date) проверяем только конкретный день.
    """
    accommodation = db.query(Accommodation).get(accommodation_id)

    if not accommodation:
        return False

    # Особый случай для gazebo (беседки) - бронирование на один день
    if accommodation.type == AccommodationType.gazebo:
        if check_in_date != check_out_date:
            return False  # Для gazebo даты должны совпадать

        # Считаем бронирования на этот день
        bookings_count = db.query(Booking).filter(
            Booking.accommodation_id == accommodation_id,
            Booking.check_in_date == check_in_date
        ).count()

        return bookings_count < accommodation.count


    # Для номеров/домов проверяем по дням
    current_date = check_in_date
    while current_date < check_out_date:
        # Считаем бронирования, которые затрагивают current_date
        bookings_count = db.query(Booking).filter(
            Booking.accommodation_id == accommodation_id,
            Booking.check_in_date <= current_date,
            Booking.check_out_date > current_date
        ).count()

        if bookings_count >= accommodation.count:
            return False

        current_date += timedelta(days=1)

    return True


def calculate_accommodation_price(
        accommodation: Accommodation,
        check_in: date,
        check_out: date,
        guests: int
) -> dict:
    """
    Рассчитывает стоимость проживания.
    Для gazebo считает как 1 день независимо от времени.
    """

    extra_beds = max(0, guests - accommodation.capacity)

    # Особый расчёт для gazebo (беседки)
    if accommodation.type == AccommodationType.gazebo:
        # Для gazebo всегда 1 день
        price = _find_price_for_date(accommodation, 0, check_in)

        return {
            "total": price,
            "nights": 0,
            "details": [{
                "date": check_in.strftime("%Y-%m-%d"),
                "type": "weekend" if check_in.weekday() >= 5 else "weekday",
                "price_on_day": price,
                "extra_beds": 0,
            }]
        }

    # Стандартный расчёт для номеров/домов
    total = 0
    details = []
    current_date = check_in
    nights = 0


    while current_date < check_out:

        price_for_day = _find_price_for_date(accommodation, extra_beds, current_date)
        details.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "type": "weekend" if current_date.weekday() >= 5 else "weekday",
            "price_on_day": price_for_day,
            "extra_beds": extra_beds,
        })

        total += price_for_day
        nights += 1
        current_date += timedelta(days=1)

    return {"total": total, "nights": nights, "details": details}


def _find_price_for_date(accommodation: Accommodation,  extra_beds:int, date: date) -> AccommodationPrice:
    """
    Вспомогальтельная функция, возвращает цену для даты с учетом типа размещения:
    - Для gazebo: цена на текущую дату (date)
    - Для номеров/домов: цена на следующий день (date + 1 день, т.к. заезд в пятницу по цене субботы)
    """
    # определяем целевую дату для расчета цены
    target_date = date if accommodation.type == AccommodationType.gazebo else date + timedelta(days=1)
    is_weekend = target_date.weekday() >= 5  # 5-6 = суббота-воскресенье

    # возвращаем сумму одного дня
    for price, extra_bed_price in accommodation.prices:
        if price.weekday_type == (Weekday.weekend if is_weekend else Weekday.weekday):
            return (price.price + (price.extra_bed_price * extra_beds))

    raise ValueError(f"No price found for {accommodation.name} on {date}")