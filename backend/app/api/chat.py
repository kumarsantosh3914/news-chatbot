from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List

from app.schemas.message import Message, MessageCreate, MessageResponse
from app.services.chat_service import chat_service

router = APIRouter()

@router.post("/sessions", response_model=str)
async def create_session():
    """Create a new chat session."""
    return chat_service.create_session()

@router.get("/sessions/{session_id}/messages", response_model=MessageResponse)
async def get_session_messages(session_id: str):
    """Get all messages for a session."""
    if not chat_service.redis_service.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return MessageResponse(messages=chat_service.get_session_messages(session_id))

@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear all messages for a session."""
    if not chat_service.redis_service.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    chat_service.clear_session(session_id)
    return {"message": "Session cleared successfully"}

@router.post("/sessions/{session_id}/messages", response_model=Message)
async def create_message(session_id: str, message: MessageCreate):
    """Process a new message and generate a response."""
    if not chat_service.redis_service.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return await chat_service.process_message(session_id, message)

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    if not chat_service.redis_service.session_exists(session_id):
        await websocket.close(code=4004, reason="Session not found")
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = MessageCreate(content=data)
            
            # Process message and get response
            response = await chat_service.process_message(session_id, message)
            
            # Send response back to client
            await websocket.send_text(response.content)
            
    except WebSocketDisconnect:
        pass 