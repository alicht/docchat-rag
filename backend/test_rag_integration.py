#!/usr/bin/env python3
"""
Integration test for RAG pipeline
This script tests the full flow: upload document -> ask question
"""

import requests
import sys
import os

BASE_URL = "http://localhost:8000"

def test_rag_pipeline():
    print("Testing RAG Pipeline Integration...")
    
    # Test 1: Upload a document
    print("\n1. Uploading test document...")
    
    test_content = """
    Machine learning is a subset of artificial intelligence (AI) that focuses on developing algorithms 
    and statistical models that enable computer systems to improve their performance on a specific task 
    through experience, without being explicitly programmed.
    
    The key characteristic of machine learning is that it learns from data. Instead of following 
    pre-programmed instructions, machine learning algorithms build mathematical models based on 
    training data to make predictions or decisions.
    
    There are three main types of machine learning:
    1. Supervised learning - uses labeled training data
    2. Unsupervised learning - finds patterns in unlabeled data  
    3. Reinforcement learning - learns through interaction with environment
    """
    
    files = {"file": ("ml_guide.txt", test_content.encode(), "text/plain")}
    
    try:
        upload_response = requests.post(f"{BASE_URL}/upload-doc", files=files)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print(f"✅ Document uploaded successfully!")
            print(f"   Document ID: {upload_data['document_id']}")
            print(f"   Chunks stored: {upload_data['chunks_stored']}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Error: {upload_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Test 2: Ask a question
    print("\n2. Testing RAG question answering...")
    
    questions = [
        "What is machine learning?",
        "What are the three types of machine learning?",
        "How does machine learning differ from traditional programming?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        
        try:
            ask_response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": question}
            )
            
            if ask_response.status_code == 200:
                ask_data = ask_response.json()
                print(f"✅ Answer received!")
                print(f"   Answer: {ask_data['answer'][:200]}...")
                print(f"   Sources: {len(ask_data['sources'])} chunks")
                
                for i, source in enumerate(ask_data['sources'][:2]):  # Show first 2 sources
                    print(f"     Source {i+1}: {source['filename']} (chunk {source['chunk_index']})")
                    
            else:
                print(f"❌ Question failed: {ask_response.status_code}")
                print(f"   Error: {ask_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Question error: {e}")
            return False
    
    print("\n🎉 RAG Pipeline test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_rag_pipeline()
    sys.exit(0 if success else 1)