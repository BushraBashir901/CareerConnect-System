from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.dependency import get_db
from app.services.conversation_service import ConversationService
from app.dependencies.rbac_strict import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# Pydantic models for API responses
class ConversationMessage(BaseModel):
    """Model for individual conversation message responses."""
    conversation_id: int
    message_type: str
    content: str
    created_at: str
    session_id: Optional[str] = None

class ConversationSession(BaseModel):
    """Model for conversation session summary responses."""
    session_id: str
    last_message: str
    last_message_time: str
    last_message_type: str

class ConversationStats(BaseModel):
    """Model for conversation statistics responses."""
    total_messages: int
    total_sessions: int
    user_messages: int
    bot_messages: int
    system_messages: int

@router.get("/history", response_model=List[ConversationMessage])
async def get_conversation_history(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve conversation history for the authenticated user.
    
    Args:
        session_id: Optional session identifier to filter messages by specific conversation
        limit: Maximum number of messages to return (default: 50, max: 200)
        db: Database session dependency
        current_user: Authenticated user from dependency injection
        
    Returns:
        List[ConversationMessage]: List of conversation messages ordered by creation time
        
    Raises:
        HTTPException: If there's an error retrieving conversation history
    """
    conversation_service = ConversationService(db)
    
    try:
        conversations = conversation_service.get_conversation_history(
            user_id=current_user.user_id,
            session_id=session_id,
            limit=limit
        )
        
        return [
            ConversationMessage(
                conversation_id=conv.conversation_id,
                message_type=conv.message_type,
                content=conv.content,
                created_at=conv.created_at.isoformat(),
                session_id=conv.session_id
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[ConversationSession])
async def get_conversation_sessions(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve recent conversation sessions for the authenticated user.
    
    Args:
        limit: Maximum number of sessions to return (default: 10, max: 50)
        db: Database session dependency
        current_user: Authenticated user from dependency injection
        
    Returns:
        List[ConversationSession]: List of recent conversation sessions with last message details
        
    Raises:
        HTTPException: If there's an error retrieving conversation sessions
    """
    conversation_service = ConversationService(db)
    
    try:
        sessions = conversation_service.get_recent_conversations(
            user_id=current_user.user_id,
            limit=limit
        )
        
        return [
            ConversationSession(
                session_id=session["session_id"],
                last_message=session["last_message"],
                last_message_time=session["last_message_time"].isoformat(),
                last_message_type=session["last_message_type"]
            )
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ConversationStats)
async def get_conversation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve conversation statistics for the authenticated user.
    
    Args:
        db: Database session dependency
        current_user: Authenticated user from dependency injection
        
    Returns:
        ConversationStats: Statistics including total messages, sessions, and message type breakdown
        
    Raises:
        HTTPException: If there's an error retrieving conversation statistics
    """
    conversation_service = ConversationService(db)
    
    try:
        stats = conversation_service.get_conversation_stats(current_user.user_id)
        
        return ConversationStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_conversation_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an entire conversation session and all its messages.
    
    Args:
        session_id: Unique identifier of the conversation session to delete
        db: Database session dependency
        current_user: Authenticated user from dependency injection
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        HTTPException: If session not found (404) or there's an error during deletion (500)
    """
    conversation_service = ConversationService(db)
    
    try:
        success = conversation_service.delete_conversation(
            user_id=current_user.user_id,
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Conversation session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
