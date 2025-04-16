from pydantic import BaseModel, validator
from typing import List, Optional
from app.utils.enums import Weekday, AccommodationType
from datetime import date, datetime, timedelta, time
from typing import Union


class AccommodationPriceSchema(BaseModel):
    weekday_type: Weekday
    price: float
    extra_bed_price: float

    class Config:
        orm_mode = True


class AccommodationSchema(BaseModel):
    id: int
    name: str
    type: AccommodationType
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image: Optional[str] = None
    capacity: int
    count: int
    check_in_time: time
    check_out_time: time
    extra_beds_available: int  # Добавили поле
    prices: List[AccommodationPriceSchema]

    # Сериализатор time → строка (при выводе)
    @validator("check_in_time", "check_out_time", check_fields=False)
    def format_time_output(cls, v: time) -> str:
        return v.strftime("%H:%M")

    class Config:
        orm_mode = True

class AccommodationShortSchema(BaseModel):
    id: int
    name: str
    type: AccommodationType
    short_description: Optional[str] = None
    capacity: int
    check_in_time: time
    check_out_time: time

    # Сериализатор time → строка (при выводе)
    @validator("check_in_time", "check_out_time", check_fields=False)
    def format_time_output(cls, v: time) -> str:
        return v.strftime("%H:%M")

    class Config:
        orm_mode = True


class AccommodationCreateSchema(BaseModel):
    name: str
    type: AccommodationType
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image: Optional[str] = None
    capacity: int
    count: int = 1
    check_in_time: time = None
    check_out_time: time = None
    extra_beds_available: int
    prices: List[AccommodationPriceSchema]

    # Автовалидация времени заселения и выселения
    @validator("check_in_time", "check_out_time", pre=True)
    def parse_time_string(cls, v: Union[str, time]) -> time:
        if isinstance(v, time):
            return v

        if isinstance(v, str):
            try:
                hours, minutes = map(int, v.split(':'))
                return time(hour=hours, minute=minutes)
            except (ValueError, AttributeError):
                pass
        raise ValueError("Time must be in 'HH:MM' format")