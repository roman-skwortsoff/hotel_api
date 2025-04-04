from sqlalchemy import Column, Integer, String, Text, ForeignKey, DECIMAL, Enum, Time
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.enums import Weekday, AccommodationType
from datetime import time


class Accommodation(Base):
    __tablename__ = "accommodations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(AccommodationType), nullable=False)
    short_description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=False)  # Основная вместимость
    count = Column(Integer, default=1)  # Количество таких номеров/домов
    check_in_time = Column(Time, default=time(15, 0))
    check_out_time = Column(Time, default=time(12, 0))
    extra_beds_available = Column(Integer, default=0)  # Количество доп. мест
    prices = relationship("AccommodationPrice", lazy="selectin", back_populates="accommodation")


class AccommodationPrice(Base):
    __tablename__ = "accommodation_prices"

    id = Column(Integer, primary_key=True, index=True)
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"))
    weekday_type = Column(Enum(Weekday), nullable=False)  # Будний или выходной
    price = Column(DECIMAL(10, 2), nullable=False)  # Основная цена
    extra_bed_price = Column(DECIMAL(10, 2), default=0.00)  # Цена за доп. место

    accommodation = relationship("Accommodation", lazy="selectin", back_populates="prices")
