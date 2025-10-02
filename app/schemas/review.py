from pydantic import BaseModel
from pydantic.types import StringConstraints
from datetime import datetime
from typing import Optional, Annotated
from app.schemas.book_service import ServiceRead
from uuid import UUID

class ReviewBase(BaseModel):
    booking_id: UUID
    rating: int
    comment: Optional[Annotated[str, StringConstraints(max_length=500)]] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[Annotated[str, StringConstraints(max_length=500)]] = None

class ReviewRead(ReviewBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    service: ServiceRead | None = None

    model_config = {"from_attributes": True}