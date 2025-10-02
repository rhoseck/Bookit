import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_routes_exist():
    """Test that the API routes are correctly registered."""
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    
    # Test auth endpoints
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "password"})
    print(f"Auth login response: {response.status_code}, {response.text}")
    
    # Test bookings endpoint
    response = client.get("/bookings/")
    print(f"Bookings response: {response.status_code}, {response.text}")
    
    # Test services endpoint
    response = client.get("/services/")
    print(f"Services response: {response.status_code}, {response.text}")