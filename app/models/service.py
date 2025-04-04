from sqlalchemy import Column, Integer, String, Text, ForeignKey, DECIMAL, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.enums import Weekday


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)
    is_free = Column(Boolean, default=False)
    is_agreement_required = Column(Boolean, default=False)

    prices = relationship("ServicePrice", lazy="selectin", back_populates="service")


class ServicePrice(Base):
    __tablename__ = "service_prices"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    name = Column(String(100), nullable=True)
    weekday_type = Column(Enum(Weekday), nullable=False)
    duration_hours = Column(DECIMAL(10, 1), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)

    service = relationship("Service", lazy="selectin", back_populates="prices")
