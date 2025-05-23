from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from app.db.session import get_db
from app.models.accommodation import Accommodation, AccommodationPrice
from app.utils.enums import AccommodationType, Weekday
from datetime import datetime
from fastapi.responses import RedirectResponse


templates = Jinja2Templates(directory="templates")


router = APIRouter(prefix="/accommodations", tags=["Accommodations"])


@router.get("/add")
def add_accommodation_page(request: Request):
    return templates.TemplateResponse("add_accommodation.html", {"request": request})


@router.post("/add")
def create_accommodation(
        request: Request,
        name: str = Form(...),
        type: AccommodationType = Form(...),
        short_description: str = Form(None),
        full_description: str = Form(None),
        image: str = Form(None),
        capacity: int = Form(...),
        count: int = Form(1),
        check_in_time: str = Form("15:00"),
        check_out_time: str = Form("12:00"),
        extra_beds_available: int = Form(0),
        weekday_price: float = Form(...),
        weekday_extra_bed_price: float = Form(0.00),
        weekend_price: float = Form(...),
        weekend_extra_bed_price: float = Form(0.00),
        db: Session = Depends(get_db)
):
    print(f"Полученные данные: name={name}, type={type}, capacity={capacity}, count={count}")
    print(f"check_in_time={check_in_time}, check_out_time={check_out_time}")
    print(f"weekday_price={weekday_price}, weekend_price={weekend_price}")

    # Преобразуем тип размещения из строки в Enum
    try:
        type = AccommodationType(type)
        print(f"Тип размещения после конвертации: {type}")
    except ValueError:
        print(f"Ошибка конвертации type: {type}")
        return {"error": "Неверный тип размещения"}

    # Преобразуем время из строки в объект time
    try:
        check_in_time = datetime.strptime(check_in_time, "%H:%M").time()
        check_out_time = datetime.strptime(check_out_time, "%H:%M").time()
        print(f"Преобразованное время: check_in_time={check_in_time}, check_out_time={check_out_time}")
    except ValueError as e:
        print(f"Ошибка конвертации времени: {e}")
        return {"error": "Неверный формат времени"}

    # Создаем объект размещения
    new_accommodation = Accommodation(
        name=name,
        type=type,
        short_description=short_description,
        full_description=full_description,
        image=image,
        capacity=capacity,
        count=count,
        check_in_time=check_in_time,
        check_out_time=check_out_time,
        extra_beds_available=extra_beds_available
    )

    print(f"Создан объект размещения: {new_accommodation}")

    db.add(new_accommodation)
    db.commit()
    db.refresh(new_accommodation)

    # Создаем цены (Будний и Выходной)
    weekday_price_entry = AccommodationPrice(
        accommodation_id=new_accommodation.id,
        weekday_type=Weekday.weekday,
        price=weekday_price,
        extra_bed_price=weekday_extra_bed_price
    )

    weekend_price_entry = AccommodationPrice(
        accommodation_id=new_accommodation.id,
        weekday_type=Weekday.weekend,
        price=weekend_price,
        extra_bed_price=weekend_extra_bed_price
    )

    print(f"Созданы цены: {weekday_price_entry}, {weekend_price_entry}")

    db.add_all([weekday_price_entry, weekend_price_entry])
    db.commit()

    print("Добавление размещения завершено.")

    return RedirectResponse(url="/accommodations/add", status_code=303)