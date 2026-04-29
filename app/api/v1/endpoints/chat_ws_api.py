from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.db.session import SessionLocal
from app.services.chatbot_service import CareerConnectChatbot
from app.core.auth import verify_token
from app.models.user import User
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
        token: Authentication token for user identification (required)
        session_id: Optional session identifier to group conversations
        
    Note:
        - Generates a new session ID if not provided
        - Requires valid JWT token for authentication
        - All messages are persisted to database (user, bot, and system messages)
        - Messages are grouped by session ID for conversation history
        
    Raises:
        WebSocketDisconnect: When client disconnects from the chat
        Exception: For internal server errors during chat processing
    """
    await websocket.accept()
    
    # Create database session for this WebSocket connection
    db = SessionLocal()
    current_user = None
    
    try:
        # Verify token and get user
        if not token:
            await websocket.close(code=4001, reason="Authentication token required")
            return
            
        try:
            payload = verify_token(token)
            if not payload:
                await websocket.close(code=4001, reason="Invalid token")
                return
                
            # Get user_id from 'sub' field (standard JWT claim)
            user_id_str = payload.get("sub")
            if not user_id_str:
                await websocket.close(code=4001, reason="Invalid token payload")
                return
                
            # Convert string to integer
            try:
                user_id = int(user_id_str)
            except ValueError:
                await websocket.close(code=4001, reason="Invalid user ID in token")
                return
                
            # Get user from database
            current_user = db.query(User).filter(User.user_id == user_id).first()
            if not current_user:
                await websocket.close(code=4001, reason="User not found")
                return
                
            print(f"Authentication successful for user: {current_user.user_id}")
                
        except Exception as auth_error:
            print(f"Authentication error: {auth_error}")
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Initialize chatbot service
        chatbot = CareerConnectChatbot(db)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Send and save welcome message
        welcome_result = chatbot.save_welcome_message(
            user_id=current_user.user_id,
            session_id=session_id
        )
        await websocket.send_text(welcome_result["welcome_text"])
        
        while True:
            try:
                # Receive message from user
                user_message = await websocket.receive_text()
                print(f"User: {user_message}")

                # Process message with saving (handles both user and bot messages)
                chat_result = await chatbot.chat_with_saving(
                    user_id=current_user.user_id,
                    message=user_message,
                    session_id=session_id
                )
                
                # Send response back to user
                await websocket.send_text(chat_result["response_text"])
                print(f"Bot: {chat_result['response_text']}")

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