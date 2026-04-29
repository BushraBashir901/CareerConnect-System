from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from app.models.chatbot_message import ChatMessage
import json
import uuid

class ConversationService:
    """Service for managing chatbot conversations and message persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_message(self, 
                    user_id: int, 
                    message_type: str, 
                    content: str, 
                    session_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """
        Save a chat message to the database.
        
        Args:
            user_id: ID of the user sending/receiving the message
            message_type: Type of message ('user', 'bot', 'system')
            content: Message content
            session_id: Optional session ID to group messages
            metadata: Optional metadata as dictionary
            
        Returns:
            Created ChatMessage record
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Convert metadata to JSON string if provided
        metadata_json = json.dumps(metadata) if metadata else None
        
        conversation = ChatMessage(
            user_id=user_id,
            message_type=message_type,
            content=content,
            session_id=session_id,
            conversation_metadata=metadata_json
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def get_conversation_history(self, 
                               user_id: int, 
                               session_id: Optional[str] = None,
                               limit: int = 50) -> List[ChatMessage]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: ID of the user
            session_id: Optional session ID to filter by
            limit: Maximum number of messages to return
            
        Returns:
            List of ChatMessage records
        """
        query = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        )
        
        if session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        
        return query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation sessions for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries with session info
        """
        # Get unique session IDs with their latest message
        result = self.db.execute(text("""
            SELECT DISTINCT ON (session_id) 
                session_id,
                content as last_message,
                created_at as last_message_time,
                message_type
            FROM chat_messages
            WHERE user_id = :user_id
            ORDER BY session_id, created_at DESC
            LIMIT :limit
        """), {"user_id": user_id, "limit": limit}).fetchall()
        
        sessions = []
        for row in result:
            sessions.append({
                "session_id": row.session_id,
                "last_message": row.last_message[:100] + "..." if len(row.last_message) > 100 else row.last_message,
                "last_message_time": row.last_message_time,
                "last_message_type": row.message_type
            })
        
        return sessions
    
    def delete_conversation(self, user_id: int, session_id: str) -> bool:
        """
        Delete an entire conversation session.
        
        Args:
            user_id: ID of the user
            session_id: Session ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        deleted_count = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.session_id == session_id
        ).delete()
        
        self.db.commit()
        return deleted_count > 0
    
    def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about a user's conversations.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with conversation statistics
        """
        total_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()
        
        total_sessions = self.db.query(ChatMessage.session_id).filter(
            ChatMessage.user_id == user_id
        ).distinct().count()
        
        user_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == 'user'
        ).count()
        
        bot_messages = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == 'bot'
        ).count()
        
        return {
            "total_messages": total_messages,
            "total_sessions": total_sessions,
            "user_messages": user_messages,
            "bot_messages": bot_messages,
            "system_messages": total_messages - user_messages - bot_messages
        }
    
    def save_conversation_pair(self, 
                             user_id: int, 
                             user_message: str, 
                             bot_response: str,
                             session_id: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> tuple[ChatMessage, ChatMessage]:
        """
        Save both user message and bot response as a pair.
        
        Args:
            user_id: ID of the user
            user_message: User's message
            bot_response: Bot's response
            session_id: Optional session ID
            metadata: Optional metadata for both messages
            
        Returns:
            Tuple of (user_conversation, bot_conversation)
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Save user message
        user_conv = self.save_message(
            user_id=user_id,
            message_type='user',
            content=user_message,
            session_id=session_id,
            metadata=metadata
        )
        
        # Save bot response
        bot_conv = self.save_message(
            user_id=user_id,
            message_type='bot',
            content=bot_response,
            session_id=session_id,
            metadata=metadata
        )
        
        return user_conv, bot_conv
