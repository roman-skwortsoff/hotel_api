from pydantic import BaseModel
from typing import List, Optional
from app.utils.enums import Weekday


class ServicePriceSchema(BaseModel):
    weekday_type: Weekday
    name: Optional[str] = None
    duration_hours: Optional[int] = None
    price: float

    class Config:
        orm_mode = True


class ServiceSchema(BaseModel):
    id: int
    name: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image: Optional[str] = None
    is_free: bool
    is_agreement_required: bool
    prices: Optional[List[ServicePriceSchema]] = None

    class Config:
        orm_mode = True

class ServiceCreateSchema(BaseModel):
    name: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    image: Optional[str] = None
    is_free: bool
    is_agreement_required: bool
    prices: Optional[List[ServicePriceSchema]] = None
