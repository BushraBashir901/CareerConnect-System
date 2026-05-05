from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.orchestrator import get_global_orchestrator
from app.core.auth import verify_token
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.conversation import ChatRequest
from app.core.logger import logger

router = APIRouter()


@router.websocket("/chat/ws")
async def chat_socket(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str = Query(...)
):

    await websocket.accept()

    db = SessionLocal()
    user = None

    try:
        # -------------------------
        # 1. AUTH
        # -------------------------
        logger.info("websocket_connection_start", 
                   extra={
                       "endpoint": "/chat/ws",
                       "session_id": session_id,
                       "has_token": bool(token)
                   })

        payload = verify_token(token)

        if not payload:
            logger.warning("websocket_auth_failed", 
                        extra={
                            "reason": "Invalid token",
                            "session_id": session_id
                        })
            await websocket.close(code=4001, reason="Invalid token")
            return

        user_id = int(payload["sub"])

        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            logger.warning("websocket_auth_failed", 
                        extra={
                            "reason": "User not found",
                            "user_id": user_id,
                            "session_id": session_id
                        })
            await websocket.close(code=4001, reason="User not found")
            return

        logger.info("websocket_auth_success", 
                   extra={
                       "user_id": user_id,
                       "session_id": session_id
                   })

        # -------------------------
        # 2. ORCHESTRATOR
        # -------------------------
        orchestrator = await get_global_orchestrator()

        # -------------------------
        # 3. MAIN LOOP
        # -------------------------
        while True:
            try:
                user_message = await websocket.receive_text()
                
                logger.info("websocket_message_received", 
                           extra={
                               "user_id": user_id,
                               "session_id": session_id,
                               "message_length": len(user_message)
                           })

                chat_request = ChatRequest(
                    message=user_message,
                    user_id=user.user_id,
                    session_id=session_id
                )

                response = await orchestrator.process_message(
                    request=chat_request
                )

                logger.info("websocket_response_sent", 
                           extra={
                               "user_id": user_id,
                               "session_id": session_id,
                               "response_length": len(response.response),
                               "response_time": response.metadata.get("processing_time", 0)
                           })

                await websocket.send_text(response.response)

            except WebSocketDisconnect:
                logger.info("websocket_disconnect", 
                           extra={
                               "user_id": user_id,
                               "session_id": session_id,
                               "reason": "normal_disconnect"
                           })
                break
                
            except Exception as e:
                logger.error("websocket_message_error", 
                            extra={
                                "user_id": user_id,
                                "session_id": session_id,
                                "error": str(e)
                            })
                await websocket.send_text(f"Error processing message: {str(e)}")

    except WebSocketDisconnect:
        logger.info("websocket_disconnect", 
                   extra={
                       "user_id": user.user_id if user else "unknown",
                       "session_id": session_id,
                       "reason": "connection_closed"
                   })

    except Exception as e:
        logger.error("websocket_internal_error", 
                    extra={
                        "session_id": session_id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
        await websocket.close(code=1011, reason="Internal error")
    
    finally:
        if db:
            db.close()