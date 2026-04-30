from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from app.models.chatbot_message import ChatMessage


class ConversationRepository:
    """Repository: ONLY database operations"""

    def __init__(self, db: Session):
        self.db = db

    def save_message(
        self,
        user_id: int,
        message_type: str,
        content: str,
        session_id: str,
        metadata: Optional[str] = None
    ) -> ChatMessage:

        message = ChatMessage(
            user_id=user_id,
            message_type=message_type,
            content=content,
            session_id=session_id,
            conversation_metadata=metadata
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message


    def get_conversation_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatMessage]:

        query = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        )

        if session_id:
            query = query.filter(ChatMessage.session_id == session_id)

        return query.order_by(desc(ChatMessage.created_at)).limit(limit).all()

    def get_recent_conversations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

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

        return [
            {
                "session_id": row.session_id,
                "last_message": (
                    row.last_message[:100] + "..."
                    if len(row.last_message) > 100
                    else row.last_message
                ),
                "last_message_time": row.last_message_time,
                "last_message_type": row.message_type
            }
            for row in result
        ]

   
    def delete_conversation(self, user_id: int, session_id: str) -> bool:

        deleted = self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.session_id == session_id
        ).delete()

        self.db.commit()
        return deleted > 0

    # -----------------------------------------------------#
    def count_messages(self, user_id: int):
        return self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()

    def count_sessions(self, user_id: int):
        return self.db.query(ChatMessage.session_id).filter(
            ChatMessage.user_id == user_id
        ).distinct().count()

    def count_user_messages(self, user_id: int):
        return self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == "user"
        ).count()

    def count_bot_messages(self, user_id: int):
        return self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == "bot"
        ).count()