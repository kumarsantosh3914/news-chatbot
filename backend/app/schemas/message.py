from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base class for message models."""
    content: str
    role: Literal["user", "assistant"] = "user"


class MessageCreate(MessageBase):
    """Model for creating a new message."""
    pass


class Message(MessageBase):
    """Model for a complete message with meta information."""
    id: str
    timestamp: datetime
    meta: Optional[Dict] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResponse(BaseModel):
    """Response model for messages."""
    messages: List[Message]


class WebSocketMessage(BaseModel):
    """Model for WebSocket message."""
    message: str


class SearchResult(BaseModel):
    """Model for vector search results."""
    id: str
    text: str
    score: float
    meta: Optional[Dict] = None