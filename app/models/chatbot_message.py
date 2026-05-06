from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Message content
    message_type = Column(String(50), nullable=False)  
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional metadata
    session_id = Column(String(255), nullable=True)  
     

    user = relationship("User", back_populates="chat_messages")

