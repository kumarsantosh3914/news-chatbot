import uuid
from datetime import datetime
from typing import List, Optional

from app.core.config import settings
from app.rag.llm import get_llm_response
from app.rag.vector_store import search_similar_articles
from app.schemas.message import Message, MessageCreate
from app.services.redis_service import redis_service

class ChatService:
    def __init__(self):
        self.redis_service = redis_service
    
    def create_session(self) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        self.redis_service.create_session(session_id)
        return session_id
    
    def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session."""
        return self.redis_service.get_session_messages(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        self.redis_service.clear_session(session_id)
    
    async def process_message(self, session_id: str, message: MessageCreate) -> Message:
        """Process a new message and generate a response."""
        # Create user message
        user_message = Message(
            id=str(uuid.uuid4()),
            content=message.content,
            role="user",
            timestamp=datetime.utcnow()
        )
        
        # Store user message
        self.redis_service.add_message(session_id, user_message)
        
        # Search for relevant articles
        relevant_articles = search_similar_articles(message.content, top_k=3)
        
        # Prepare context from relevant articles
        context = "\n\n".join([article.text for article in relevant_articles])
        
        # Generate response using LLM
        response_content = await get_llm_response(message.content, context)
        
        # Create assistant message
        assistant_message = Message(
            id=str(uuid.uuid4()),
            content=response_content,
            role="assistant",
            timestamp=datetime.utcnow(),
            meta={"relevant_articles": [article.id for article in relevant_articles]}
        )
        
        # Store assistant message
        self.redis_service.add_message(session_id, assistant_message)
        
        return assistant_message

# Create a singleton instance
chat_service = ChatService() 