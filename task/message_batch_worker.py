from typing import List, Dict, Any
from celery_worker import celery_app
from app.db.session import SessionLocal
from app.repositories.chatbot_repo.conversation_repo import ConversationRepository


@celery_app.task
def save_messages_batch(user_id: int, session_id: str, messages: List[Dict[str, Any]]) -> bool:
    
    db = SessionLocal()
    try:
        repo = ConversationRepository(db)

        for message in messages:
            repo.save_message(
                user_id=user_id,
                message_type=message["role"],
                content=message["content"],
                session_id=session_id
            )

        return True

    except Exception as e:
        db.rollback()
        print(f"[Celery Error] save_messages_batch: {e}")
        return False

    finally:
        db.close()