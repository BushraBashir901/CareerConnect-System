from pydantic import BaseModel
from typing import Optional


class ConversationMessage(BaseModel):
    conversation_id: int
    message_type: str
    content: str
    created_at: str
    session_id: Optional[str] = None


class ConversationSession(BaseModel):
    session_id: str
    last_message: str
    last_message_time: str
    last_message_type: str


class ConversationStats(BaseModel):
    total_messages: int
    total_sessions: int
    user_messages: int
    bot_messages: int
    system_messages: int

    model_config = {
        "from_attributes": True
    }