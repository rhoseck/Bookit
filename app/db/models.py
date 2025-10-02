from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base
from datetime import datetime, timezone
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    CUSTOMER = "user"  # alias for backward compatibility with tests

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Add relationships
    reviews = relationship("Review", back_populates="user")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())
    
    # Add relationship to bookings
    bookings = relationship("Booking", back_populates="service")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Add relationships
    service = relationship("Service", back_populates="bookings")
    reviews = relationship("Review", back_populates="booking")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Add relationships
    booking = relationship("Booking", back_populates="reviews")
    user = relationship("User", back_populates="reviews")