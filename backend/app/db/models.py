from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)
    
    session = relationship("Session", back_populates="messages") 