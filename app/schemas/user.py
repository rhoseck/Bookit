from pydantic import BaseModel, constr, EmailStr
from typing import Annotated
from enum import Enum
from datetime import datetime
from uuid import UUID

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    CUSTOMER = "user"  # alias for backwards compatibility

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: Annotated[str, constr(min_length=8, max_length=72)]

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: Annotated[str, constr(min_length=8, max_length=72)] | None = None

class UserRead(UserBase):
    id: UUID
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}