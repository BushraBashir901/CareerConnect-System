from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.db.session import SessionLocal
from app.services.chatbot_service import CareerConnectChatbot
from typing import Optional
import uuid

router = APIRouter()

@router.websocket("/chat")
async def chat_socket(
    websocket: WebSocket, 
    token: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time chat with CareerConnect AI assistant.
    
    Establishes a WebSocket connection for interactive chat sessions with the AI chatbot.
    Handles message exchange, error management, and connection lifecycle.
    
    Args:
        websocket: WebSocket connection instance
        token: Optional authentication token for user identification
        session_id: Optional session identifier to group conversations
        
    Note:
        - Generates a new session ID if not provided
        - Currently operates without authentication (token parameter unused)
        - Messages are not persisted to database in current implementation
        
    Raises:
        WebSocketDisconnect: When client disconnects from the chat
        Exception: For internal server errors during chat processing
    """
    await websocket.accept()
    
    # Create database session for this WebSocket connection
    db = SessionLocal()
    current_user = None
    
    try:
        # Initialize PydanticAI chatbot
        chatbot = CareerConnectChatbot(db)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Send welcome message
        await websocket.send_text("Hello! I'm your CareerConnect AI assistant. How can I help you with your career today?")
        
        while True:
            try:
                user_message = await websocket.receive_text()
                print(f"User: {user_message}")

                bot_response = await chatbot.chat(user_message)
                print(f"Bot: {bot_response}")

                await websocket.send_text(bot_response)

            except Exception as chat_error:
                print(f"Chat error: {chat_error}")
                error_message = "Sorry, I encountered an error processing your message. Please try again."
                await websocket.send_text(error_message)
                

    except WebSocketDisconnect:
        print("Client disconnected from chat")
        if current_user:
            print(f"User {current_user.user_id} disconnected from session {session_id}")
    except Exception as e:
        print(f"Error in chat socket: {e}")
        await websocket.close(code=1011, reason="Internal server error")
    finally:
     
        db.close()