"""
Message repository for database operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.chatbot_message import ChatMessage


class MessageRepository:
    """Repository for chat message operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save_message(self, session_id: str, message_type: str, content: str, 
                        user_id: int, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Save a message to database."""
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            user_id=user_id,
            created_at=datetime.utcnow(),
            conversation_metadata=str(metadata) if metadata else None
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
        
        return [
            {
                "role": msg.message_type,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    
    async def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit).all()
        
        return [
            {
                "session_id": msg.session_id,
                "message_type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    
    async def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for user conversations."""
        total_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()
        
        user_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == "user"
        ).count()
        
        bot_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == "bot"
        ).count()
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "bot_messages": bot_messages,
            "sessions": len(set(
                msg.session_id for msg in self.db.query(ChatMessage).filter(
                    ChatMessage.user_id == user_id
                ).all()
            ))
        }
