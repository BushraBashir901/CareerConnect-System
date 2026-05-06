from pydantic import BaseModel
from typing import Optional, Dict, Any


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


# Chat schemas for WebSocket communication
class ChatRequest(BaseModel):
    message: str
    user_id: int
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None