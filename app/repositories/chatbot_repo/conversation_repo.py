from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.chatbot_message import ChatMessage
class ConversationRepository:
  

    def __init__(self, db: Session):
        self.db = db


    def save_message(
        self,
        user_id: int,
        message_type: str,
        content: str,
        session_id: str,
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

  
    def get_conversation_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        messages = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id
            )
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )

        return [
            {
                "role": "assistant" if msg.message_type == "bot" else "user",
                "content": msg.content
            }
            for msg in messages
        ]

 
    def delete_conversation(
        self,
        user_id: int,
        session_id: str
    ) -> bool:

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