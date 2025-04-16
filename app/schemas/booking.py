from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic.networks import EmailStr

from app.schemas.accommodation import AccommodationSchema, AccommodationShortSchema


class BookingResponseSchema(BaseModel):
    id: int
    accommodation_id: int
    check_in_date: date
    check_out_date: date
    guests: int
    guest_name: str
    guest_phone: str
    guest_email: EmailStr
    notes: Optional[str] = None
    total_price: float
    created_at: datetime
    accommodation: AccommodationShortSchema

    class Config:
        orm_mode = True

class BookingCreateSchema(BaseModel):
    accommodation_id: int
    check_in_date: date
    check_out_date: date
    guests: int = Field(..., gt=0, description="Количество гостей")
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