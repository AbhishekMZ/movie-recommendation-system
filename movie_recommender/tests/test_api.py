from fastapi.testclient import TestClient
from api.main import app
import pytest
import json

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_register_user():
    """Test user registration"""
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    assert "id" in response.json()
    assert "username" in response.json()

def test_login():
    """Test user login"""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_get_recommendations():
    """Test getting recommendations"""
    # First login to get token
    login_response = client.post("/auth/login", 
        json={"username": "testuser", "password": "testpass123"})
    token = login_response.json()["access_token"]
    
    # Test recommendations endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/recommendations", headers=headers)
    assert response.status_code == 200
    recommendations = response.json()
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(r, dict) for r in recommendations)

def test_submit_rating():
    """Test submitting a rating"""
    # First login to get token
    login_response = client.post("/auth/login", 
        json={"username": "testuser", "password": "testpass123"})
    token = login_response.json()["access_token"]
    
    # Test rating submission
    headers = {"Authorization": f"Bearer {token}"}
    rating_data = {
        "content_id": "C1",
        "rating": 4.5
    }
    response = client.post("/ratings", json=rating_data, headers=headers)
    assert response.status_code == 201
    assert "message" in response.json()

if __name__ == "__main__":
    pytest.main([__file__])
