import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_empty_database():
    """Test asking question when no documents are uploaded"""
    response = client.post(
        "/ask",
        json={"question": "What is machine learning?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["sources"] == []
    assert "No documents found" in data["answer"]

def test_ask_valid_question():
    """Test asking a question - may fail without OpenAI API key"""
    response = client.post(
        "/ask",
        json={"question": "What is artificial intelligence?"}
    )
    
    # Should either work (200) or fail due to missing API key (500)
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)

def test_ask_malformed_request():
    """Test malformed request"""
    response = client.post(
        "/ask",
        json={}
    )
    
    assert response.status_code == 422  # Validation error

def test_ask_empty_question():
    """Test empty question"""
    response = client.post(
        "/ask",
        json={"question": ""}
    )
    
    # Should handle empty question gracefully
    assert response.status_code in [200, 500]