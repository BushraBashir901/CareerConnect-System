from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.chatbot_message import ChatMessage
from app.repositories.chatbot_repo.conversation_repo import ConversationRepository
import uuid
import json


class ConversationService:
    """Service: business logic + orchestration"""

    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)

    def save_message(
        self,
        user_id: int,
        message_type: str,
        content: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:

        if not session_id:
            session_id = str(uuid.uuid4())

        metadata_json = json.dumps(metadata) if metadata else None

        return self.repo.save_message(
            user_id=user_id,
            message_type=message_type,
            content=content,
            session_id=session_id,
            metadata=metadata_json
        )


    def save_conversation_pair(
        self,
        user_id: int,
        user_message: str,
        bot_response: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[ChatMessage, ChatMessage]:

        if not session_id:
            session_id = str(uuid.uuid4())

        user_msg = self.repo.save_message(
            user_id=user_id,
            message_type="user",
            content=user_message,
            session_id=session_id,
            metadata=json.dumps(metadata) if metadata else None
        )

        bot_msg = self.repo.save_message(
            user_id=user_id,
            message_type="bot",
            content=bot_response,
            session_id=session_id,
            metadata=json.dumps(metadata) if metadata else None
        )

        return user_msg, bot_msg

    def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:

        total_messages = self.repo.count_messages(user_id)
        total_sessions = self.repo.count_sessions(user_id)
        user_messages = self.repo.count_user_messages(user_id)
        bot_messages = self.repo.count_bot_messages(user_id)

        return {
            "total_messages": total_messages,
            "total_sessions": total_sessions,
            "user_messages": user_messages,
            "bot_messages": bot_messages,
            "system_messages": total_messages - user_messages - bot_messages
        }