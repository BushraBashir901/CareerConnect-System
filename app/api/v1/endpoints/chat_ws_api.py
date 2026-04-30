from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.chatbot_service import CareerConnectChatbot
from app.core.auth import verify_token
from app.models.user import User

router = APIRouter()


@router.websocket("/chat/ws")
async def chat_socket(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str = Query(...)
):
    await websocket.accept()

    db: Session = SessionLocal()
    current_user = None

    try:
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return

        user_id = int(payload["sub"])

        current_user = db.query(User).filter(User.user_id == user_id).first()
        if not current_user:
            await websocket.close(code=4001, reason="User not found")
            return

        chatbot = CareerConnectChatbot(db)

        welcome = chatbot.save_welcome_message(
            user_id=current_user.user_id,
            session_id=session_id
        )

        await websocket.send_text(welcome.content)

        while True:
            user_message = await websocket.receive_text()

            result = await chatbot.chat_with_saving(
                user_id=current_user.user_id,
                message=user_message,
                session_id=session_id
            )

            await websocket.send_text(result["response"])


    except WebSocketDisconnect:
        print(f"User disconnected: {current_user.user_id if current_user else 'Unknown'}")

    except Exception as e:
        print("WebSocket Error:", e)
        await websocket.close(code=1011, reason="Internal error")

    finally:
        db.close()
