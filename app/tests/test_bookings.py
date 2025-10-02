import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.db.models import User, Service, Booking
from app.services.auth import hash_password, create_access_token
from datetime import datetime, timedelta
from fastapi import HTTPException

# Using fixtures from conftest.py

@pytest.fixture
def user(db: Session):
    # Create a test user directly with a known password
    from app.services.auth import hash_password
    from app.db.models import User, UserRole
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
    
    # Create new user with properly hashed password
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hash_password("securepassword123"),
        role=UserRole.CUSTOMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_token(user: User):
    # Create a token directly using the auth service
    from app.services.auth import create_access_token
    
    # Create token for the user
    token = create_access_token(data={"sub": str(user.id)})
    return token

@pytest.fixture
def service(db: Session):
    service = Service(
        name="Test Service",
        description="Test Description",
        price=100.0,
        duration_minutes=60,
        is_active=True
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def test_create_booking_conflict(db: Session, user: User, service: Service):
    # Test directly with the repository function instead of using the API
    from app.repositories import booking_repo
    from app.schemas.booking import BookingCreate
    
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    # Create booking data
    booking_data = BookingCreate(
        service_id=service.id,
        start_time=start_time,
        end_time=end_time
    )
    
    # Create first booking directly with repository
    db_booking = booking_repo.create_booking(db, booking_data, user.id)
    assert db_booking.id is not None, "Booking should be created successfully"
    assert db_booking.status == "pending", "Booking status should be set to pending"
    
    # Try to create a conflicting booking using the service layer
    from app.services.booking import create_booking
    
    try:
        booking2 = create_booking(db, booking_data, user.id)
        assert False, "Should have raised an HTTPException for conflicting booking"
    except HTTPException as e:
        assert e.status_code == 409, f"Expected conflict error with status code 409, got {e.status_code}"
        assert "already booked" in e.detail, f"Expected 'already booked' in error detail, got {e.detail}"