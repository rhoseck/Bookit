from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.services import booking as booking_service
from app.services.auth import get_current_user
from datetime import datetime
from app.db.models import User
from typing import List, Optional
from uuid import UUID

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return booking_service.create_booking(db, booking, current_user.id)

@router.get("/me", response_model=List[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return booking_service.get_user_bookings(db, current_user.id)

@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    status: Optional[str] = None,
    start_from: Optional[datetime] = None,
    end_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return booking_service.get_all_bookings(db, status, start_from, end_to)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return booking_service.get_booking(db, booking_id, current_user)

@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: UUID,
    booking_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can update bookings")
    return booking_service.update_booking(db, booking_id, booking_in, current_user)

@router.delete("/{booking_id}", status_code=204)
def delete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete bookings")
    booking_service.delete_booking(db, booking_id, current_user)
    return None