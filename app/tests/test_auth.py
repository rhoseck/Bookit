import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.services.security import hash_password
from app.db.models import User

# Using fixtures from conftest.py

@pytest.fixture
def user(db: Session):
    # First register a user through the API to ensure proper password hashing
    from app.schemas.user import UserCreate
    from app.repositories.user_repo import create_user
    
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="securepassword123"
    )
    
    user = create_user(db, user_data)
    return user

def test_register_and_login(client: TestClient, db: Session):
    # Register
    response = client.post(
        "/auth/register",
        json={"name": "Test User 2", "email": "test2@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test2@example.com"

    # Login
    response = client.post(
        "/auth/login",
        data={"username": "test2@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_unauthorized_access(client: TestClient):
    response = client.get("/bookings")
    assert response.status_code == 401