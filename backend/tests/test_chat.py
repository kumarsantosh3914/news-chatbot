import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chat_service import chat_service

client = TestClient(app)

def test_create_session():
    response = client.post("/api/v1/chat/sessions")
    assert response.status_code == 200
    session_id = response.json()
    assert isinstance(session_id, str)
    assert len(session_id) > 0

def test_get_session_messages():
    # Create a session first
    response = client.post("/api/v1/chat/sessions")
    session_id = response.json()
    
    # Get messages
    response = client.get(f"/api/v1/chat/sessions/{session_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert isinstance(data["messages"], list)

def test_clear_session():
    # Create a session first
    response = client.post("/api/v1/chat/sessions")
    session_id = response.json()
    
    # Clear session
    response = client.delete(f"/api/v1/chat/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Session cleared successfully"

def test_send_message():
    # Create a session first
    response = client.post("/api/v1/chat/sessions")
    session_id = response.json()
    
    # Send a message
    response = client.post(
        f"/api/v1/chat/sessions/{session_id}/messages",
        json={"content": "What's the latest news?", "role": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "role" in data
    assert data["role"] == "assistant"

def test_invalid_session():
    # Try to get messages for non-existent session
    response = client.get("/api/v1/chat/sessions/invalid-session/messages")
    assert response.status_code == 404
    
    # Try to clear non-existent session
    response = client.delete("/api/v1/chat/sessions/invalid-session")
    assert response.status_code == 404
    
    # Try to send message to non-existent session
    response = client.post(
        "/api/v1/chat/sessions/invalid-session/messages",
        json={"content": "Test message", "role": "user"}
    )
    assert response.status_code == 404 