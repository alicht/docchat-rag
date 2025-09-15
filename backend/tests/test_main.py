import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_endpoint():
    """Test the /ask endpoint returns expected dummy response"""
    response = client.post(
        "/ask",
        json={"question": "What is the meaning of life?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Hello from backend"

def test_ask_endpoint_validation():
    """Test the /ask endpoint validates input correctly"""
    response = client.post(
        "/ask",
        json={}
    )
    
    assert response.status_code == 422

def test_ask_endpoint_with_empty_question():
    """Test the /ask endpoint accepts empty string question"""
    response = client.post(
        "/ask",
        json={"question": ""}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Hello from backend"

def test_root_endpoint():
    """Test the root endpoint is accessible"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "DocChat RAG API is running"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"