from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.chatbot_message import ChatMessage


class ConversationRepository:
    """
    Repository layer:
    ONLY database operations (clean + predictable)
    """

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # SAVE MESSAGE
    # -------------------------
    def save_message(
        self,
        user_id: int,
        message_type: str,
        content: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:

        message = ChatMessage(
            user_id=user_id,
            message_type=message_type,
            content=content,
            session_id=session_id
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    # -------------------------
    # GET HISTORY (FOR LLM)
    # -------------------------
    def get_conversation_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:

        query = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id
            )
            .order_by(ChatMessage.created_at.asc())   # ✅ FIXED ORDER
            .limit(limit)
        )

        messages = query.all()

        return [
            {
                "role": self._normalize_role(msg.message_type),
                "content": msg.content
            }
            for msg in messages
        ]

    # -------------------------
    # RECENT SESSIONS
    # -------------------------
    def get_recent_conversations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        subquery = (
            self.db.query(
                ChatMessage.session_id,
                func.max(ChatMessage.created_at).label("last_time")
            )
            .filter(ChatMessage.user_id == user_id)
            .group_by(ChatMessage.session_id)
            .subquery()
        )

        results = (
            self.db.query(ChatMessage)
            .join(
                subquery,
                (ChatMessage.session_id == subquery.c.session_id) &
                (ChatMessage.created_at == subquery.c.last_time)
            )
            .order_by(subquery.c.last_time.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "session_id": msg.session_id,
                "last_message": (
                    msg.content[:100] + "..."
                    if len(msg.content) > 100
                    else msg.content
                ),
                "last_message_time": msg.created_at,
                "last_message_type": self._normalize_role(msg.message_type)
            }
            for msg in results
        ]

    # -------------------------
    # DELETE SESSION
    # -------------------------
    def delete_conversation(self, user_id: int, session_id: str) -> bool:

        deleted = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id
            )
            .delete()
        )

        self.db.commit()
        return deleted > 0

    # -------------------------
    # COUNTS (FIXED)
    # -------------------------
    def count_messages(self, user_id: int):
        return self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()

    def count_sessions(self, user_id: int):
        return (
            self.db.query(ChatMessage.session_id)
            .filter(ChatMessage.user_id == user_id)
            .distinct()
            .count()
        )

    def count_by_role(self, user_id: int, role: str):
        return self.db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.message_type == role
        ).count()

    # -------------------------
    # INTERNAL HELPER
    # -------------------------
    def _normalize_role(self, role: str) -> str:
        """
        Ensures LLM-compatible roles
        """
        if role == "bot":
            return "assistant"
        return role