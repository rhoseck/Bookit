from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.book_service import ServiceRead
from uuid import UUID

class ReviewBase(BaseModel):
    booking_id: UUID
    rating: int
    comment: Optional[str] = Field(None, max_length=500)

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = Field(None, max_length=500)

class ReviewRead(ReviewBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    service: ServiceRead | None = None

    model_config = {"from_attributes": True}