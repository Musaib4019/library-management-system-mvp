import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, SessionLocal
import models

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_read_main():
    response = client.get("/dashboard/stats")
    assert response.status_code == 401 # Should be unauthorized without token

def test_login_wrong_credentials():
    response = client.post(
        "/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_admin():
    response = client.post(
        "/login",
        data={"username": "admin@library.edu", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_dashboard_stats():
    # Login
    res = client.post("/login", data={"username": "admin@library.edu", "password": "password123"})
    token = res.json()["access_token"]
    
    # Get stats
    response = client.get("/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_books" in data
    assert "available_copies" in data

def test_create_book_unauthorized():
    response = client.post("/books", json={
        "title": "Test Book", "author": "Test Author", "isbn": "1234567890", 
        "category": "Test", "publisher": "Test Pub", "year": 2024, "description": "", "total_copies": 1
    })
    assert response.status_code == 401
