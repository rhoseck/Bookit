from sqlalchemy.orm import Session
from app.db import models
from app.schemas.booking import BookingCreate
from datetime import datetime
from uuid import UUID

def create_booking(db: Session, booking: BookingCreate, user_id: UUID | str):
    db_booking = models.Booking(
        user_id=user_id,
        service_id=booking.service_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status="pending"  # Set a default status
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_user_bookings(db: Session, user_id: int):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()

def get_all_bookings(db: Session):
    return db.query(models.Booking).all()

def update_booking_status(db: Session, booking_id: int, status: str):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        booking.status = status
        db.commit()
        db.refresh(booking)
    return booking
