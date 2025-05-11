import json
from typing import List, Optional
import redis
from datetime import datetime

from app.core.config import settings
from app.schemas.message import Message

class RedisService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    def _get_session_key(self, session_id: str) -> str:
        return f"session:{session_id}"
    
    def create_session(self, session_id: str) -> None:
        """Create a new session with TTL."""
        self.redis.setex(
            self._get_session_key(session_id),
            settings.SESSION_TTL,
            json.dumps([])
        )
    
    def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session."""
        key = self._get_session_key(session_id)
        data = self.redis.get(key)
        if not data:
            return []
        
        messages = json.loads(data)
        return [Message(**msg) for msg in messages]
    
    def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to the session and update TTL."""
        key = self._get_session_key(session_id)
        data = self.redis.get(key)
        messages = json.loads(data) if data else []
        
        # Convert message to dict and ensure datetime is serializable
        message_dict = message.model_dump()
        message_dict["timestamp"] = message_dict["timestamp"].isoformat()
        
        messages.append(message_dict)
        
        # Store updated messages with TTL
        self.redis.setex(
            key,
            settings.SESSION_TTL,
            json.dumps(messages)
        )
    
    def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        key = self._get_session_key(session_id)
        self.redis.delete(key)
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return bool(self.redis.exists(self._get_session_key(session_id)))

# Create a singleton instance
redis_service = RedisService() 