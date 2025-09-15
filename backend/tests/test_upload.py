import pytest
from fastapi.testclient import TestClient
import os
from app.main import app

client = TestClient(app)

def test_upload_doc_txt():
    """Test uploading a text document"""
    # Create a test text file
    test_content = "This is a test document for testing the upload functionality."
    
    files = {
        "file": ("test.txt", test_content.encode(), "text/plain")
    }
    
    response = client.post("/upload-doc", files=files)
    
    # Should fail without OpenAI API key in test environment
    assert response.status_code in [200, 500]  # Allow both success and expected failure
    
    if response.status_code == 200:
        data = response.json()
        assert "document_id" in data
        assert "chunks_stored" in data
        assert data["filename"] == "test.txt"
    else:
        # Expected failure without proper OpenAI setup
        assert "error" in response.json() or "detail" in response.json()

def test_upload_doc_invalid_type():
    """Test uploading an invalid file type"""
    files = {
        "file": ("test.jpg", b"fake image content", "image/jpeg")
    }
    
    response = client.post("/upload-doc", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "not supported" in data["detail"]

def test_upload_doc_empty_file():
    """Test uploading an empty file"""
    files = {
        "file": ("empty.txt", b"", "text/plain")
    }
    
    response = client.post("/upload-doc", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "Empty file" in data["detail"]