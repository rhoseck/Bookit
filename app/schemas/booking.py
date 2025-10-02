# app/schemas/booking.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from app.schemas.book_service import ServiceRead
from uuid import UUID


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class BookingBase(BaseModel):
    service_id: UUID
    start_time: datetime
    end_time: datetime


class BookingCreate(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: UUID
    user_id: UUID
    status: BookingStatus
    service: ServiceRead  # ✅ include nested service info
    
    model_config = {"from_attributes": True}


class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None