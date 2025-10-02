# app/schemas/book_service.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ServiceBase(BaseModel):
    name: str
    description: str
    price: float
    duration_minutes: int
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceRead(ServiceBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None
