from sqlalchemy import (Date, DateTime, Column, Integer, String,
                        Text, ForeignKey, DECIMAL, Boolean, Enum)
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"))
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    guest_name = Column(String(255), nullable=False)
    guest_phone = Column(String(50), nullable=False)
    guest_email = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    accommodation = relationship("Accommodation", lazy="selectin")