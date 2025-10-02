import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.db.models import User, Service, Booking
from app.services.security import hash_password
from datetime import datetime, timedelta, timezone

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
def admin_user(db: Session):
    # Create an admin user
    from app.services.auth import hash_password
    from app.db.models import User, UserRole
    
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_user:
        return existing_user
    
    # Create new admin user with properly hashed password
    admin = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=hash_password("adminpassword123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def admin_user(db: Session):
    # Create admin user directly
    user = User(
        name="Admin User",
        email="admin@example.com",
        hashed_password=hash_password("securepassword123"),
        role="admin"
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
def admin_auth_token(admin_user: User):
    # Create a token directly using the auth service
    from app.services.auth import create_access_token
    
    # Create token for the admin user
    token = create_access_token(data={"sub": str(admin_user.id)})
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

@pytest.fixture
def completed_booking(db: Session, user: User, service: Service):
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    booking = Booking(
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="completed"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@pytest.fixture
def pending_booking(db: Session, user: User, service: Service):
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    booking = Booking(
        user_id=user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="pending"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def test_create_review(authenticated_client: TestClient, completed_booking: Booking):
    response = authenticated_client.post(
        "/reviews/",
        json={
            "booking_id": str(completed_booking.id),
            "rating": 5,
            "comment": "Great service!"
        }
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 5
    assert response.json()["comment"] == "Great service!"

def test_create_review_non_completed_booking(authenticated_client: TestClient, pending_booking: Booking):
    response = authenticated_client.post(
        "/reviews/",
        json={
            "booking_id": str(pending_booking.id),
            "rating": 5,
            "comment": "Great service!"
        }
    )
    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()

def test_delete_review_by_admin(authenticated_client: TestClient, admin_user: User, completed_booking: Booking):
    # Override the dependency to use admin user
    from app.services.auth import get_current_user
    from app.main import app
    
    # Store the original dependency
    original_dependency = app.dependency_overrides.get(get_current_user, None)
    
    # Override the dependency to return our admin user
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    try:
        # Create a review first
        response = authenticated_client.post(
            "/reviews/",
            json={
                "booking_id": str(completed_booking.id),
                "rating": 5,
                "comment": "Great service!"
            }
        )
        review_id = response.json()["id"]
        
        # Admin deletes the review
        response = authenticated_client.delete(
            f"/reviews/{review_id}/"
        )
        assert response.status_code == 204
    finally:
        # Restore the original dependency
        if original_dependency:
            app.dependency_overrides[get_current_user] = original_dependency
        else:
            del app.dependency_overrides[get_current_user]