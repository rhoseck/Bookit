# app/schemas/book_service.py
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None
