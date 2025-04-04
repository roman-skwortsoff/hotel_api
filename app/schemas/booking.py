from pydantic import BaseModel
from typing import List, Optional

from pydantic.datetime_parse import date
from pydantic.networks import EmailStr

from app.schemas.accommodation import AccommodationSchema


class BookingCreateSchema(BaseModel):
    accommodation_id: int
    check_in_date: date
    check_out_date: date
    guest_name: str
    guest_phone: str
    guest_email: EmailStr
    notes: Optional[str] = None
    total_price: float


class AvailableAccommodationSchema(BaseModel):
    accommodation: AccommodationSchema
    total_price: float
    nights: int
    requires_extra_bed: bool
    prices: List[dict]  # Подробная информация по ценам за каждую ночь

    class Config:
        orm_mode = True