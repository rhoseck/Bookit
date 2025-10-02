# app/services/booking.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.repositories import booking_repo
from app.db.models import Booking, Service, User
from uuid import UUID
from fastapi import HTTPException



def create_booking(db: Session, booking: BookingCreate, user_id: UUID) -> BookingResponse:
    from sqlalchemy.orm import joinedload
    
    # ✅ check service exists
    service = db.query(Service).filter(Service.id == booking.service_id, Service.is_active == True).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found or inactive")

    # ✅ optional: validate time logic
    if booking.end_time <= booking.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    # ✅ check for overlapping bookings
    overlap = (
        db.query(Booking)
        .filter(
            Booking.service_id == service.id,
            Booking.start_time < booking.end_time,
            Booking.end_time > booking.start_time,
        )
        .first()
    )
    if overlap:
        raise HTTPException(status_code=409, detail="Service already booked for this time slot")

    # ✅ create booking via repo
    db_booking = booking_repo.create_booking(db, booking, user_id)
    
    # ✅ explicitly load the service relationship
    db_booking = (
        db.query(Booking)
        .filter(Booking.id == db_booking.id)
        .options(joinedload(Booking.service))
        .first()
    )
    
    if not db_booking:
        raise HTTPException(status_code=500, detail="Error creating booking")

    return BookingResponse.model_validate(db_booking)


def get_booking(db: Session, booking_id: UUID, current_user: User) -> BookingResponse:
    from sqlalchemy.orm import joinedload
    
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .options(joinedload(Booking.service))  # Eagerly load the service relationship
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return BookingResponse.model_validate(booking)


def update_booking(db: Session, booking_id: UUID, booking_in: BookingUpdate, current_user: User) -> BookingResponse:
    from sqlalchemy.orm import joinedload
    
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .options(joinedload(Booking.service))
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check basic authorization
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Handle user updates
    if current_user.role == "user":
        # Users can only update pending or confirmed bookings
        if booking.status not in ["pending", "confirmed"]:
            raise HTTPException(
                status_code=400, 
                detail="Cannot modify completed or cancelled booking"
            )

        # Handle rescheduling
        if booking_in.start_time or booking_in.end_time:
            # Both times must be provided together
            if not (booking_in.start_time and booking_in.end_time):
                raise HTTPException(
                    status_code=400,
                    detail="Both start_time and end_time must be provided when rescheduling"
                )

            # Validate time order
            if booking_in.end_time <= booking_in.start_time:
                raise HTTPException(
                    status_code=400,
                    detail="End time must be after start time"
                )

            # Check for overlapping bookings
            overlap = (
                db.query(Booking)
                .filter(
                    Booking.service_id == booking.service_id,
                    Booking.id != booking.id,  # Exclude current booking
                    Booking.status.in_(["pending", "confirmed"]),  # Only check active bookings
                    Booking.start_time < booking_in.end_time,
                    Booking.end_time > booking_in.start_time,
                )
                .first()
            )
            if overlap:
                raise HTTPException(
                    status_code=409,
                    detail="Service already booked for this time slot"
                )

            booking.start_time = booking_in.start_time
            booking.end_time = booking_in.end_time

        # Handle cancellation
        if booking_in.status:
            if booking_in.status != "cancelled":
                raise HTTPException(
                    status_code=400,
                    detail="Users can only change status to cancelled"
                )
            booking.status = "cancelled"

    # Handle admin updates
    elif current_user.role == "admin":
        # Admins can update status
        if booking_in.status:
            booking.status = booking_in.status
            
        # Admins can also reschedule if needed
        if booking_in.start_time and booking_in.end_time:
            if booking_in.end_time <= booking_in.start_time:
                raise HTTPException(
                    status_code=400,
                    detail="End time must be after start time"
                )
            booking.start_time = booking_in.start_time
            booking.end_time = booking_in.end_time

    db.commit()
    db.refresh(booking)
    
    return BookingResponse.model_validate(booking)


def delete_booking(db: Session, booking_id: UUID, current_user: User) -> bool:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role == "user":
        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if booking.start_time <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Cannot delete a booking that has started")

    db.delete(booking)
    db.commit()
    return True
    
def get_user_bookings(db: Session, user_id: UUID) -> list[BookingResponse]:
    """Get all bookings for a specific user."""
    from sqlalchemy.orm import joinedload
    
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .options(joinedload(Booking.service))  # Eagerly load the service relationship
        .all()
    )
    return [BookingResponse.model_validate(booking) for booking in bookings]

def get_all_bookings(
    db: Session, 
    status: str | None = None, 
    start_from: datetime | None = None,
    end_to: datetime | None = None
) -> list[BookingResponse]:
    """Get all bookings with optional filters."""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Booking).options(joinedload(Booking.service))
    
    if status:
        query = query.filter(Booking.status == status)
    if start_from:
        query = query.filter(Booking.start_time >= start_from)
    if end_to:
        query = query.filter(Booking.end_time <= end_to)
        
    bookings = query.all()
    return [BookingResponse.model_validate(booking) for booking in bookings]
    db.commit()
    return True

def get_all_bookings(
    db: Session,
    status: str = None,
    start_from: datetime = None,
    end_to: datetime = None
    ):
    query = db.query(Booking)
    if status:
        query = query.filter(Booking.status == status)
    if start_from:
        query = query.filter(Booking.start_time >= start_from)
    if end_to:
        query = query.filter(Booking.end_time <= end_to)
    return query.all()
