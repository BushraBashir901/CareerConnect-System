from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.chatbot_tools.prompts import GENERAL_CHAT_PROMPT
from app.core.container import Container
from app.utils.timestamp import start_timer, end_timer


class CareerConnectChatbot:
   

    def __init__(self, db: Optional[Session] = None):
        self.db = db

        start = start_timer()
        self.container = Container(db) if db else None
        end_timer(start, "Container initialization")

        self.handlers = self.container.get_handlers() if self.container else None
        self.message_parser = self.container.get_parser() if self.container else None
        self.conversation_service = self.container.get_conversation_service() if self.container else None
        self.llm_service = self.container.get_llm_service() if self.container else None

    # MAIN CHAT FLOW
    async def chat(self, message: str, context: Dict[str, Any] = None) -> str:
        try:
            if not self.message_parser:
                return await self._handle_general_conversation(message)

            category, extracted_info = self.message_parser.categorize_message(message)

            if category == "job_search":
                return await self.handlers.handle_job_search(extracted_info, context)

            elif category == "interview":
                return await self.handlers.handle_interview(extracted_info)

            elif category == "career_advice":
                return await self.handlers.handle_career_advice(extracted_info)

            elif category == "skill_development":
                return await self.handlers.handle_skill_development(extracted_info)

            else:
                return await self._handle_general_conversation(message)

        except Exception as e:
            print(f"Chat error: {e}")
            return "Sorry, something went wrong. Please try again."


    # GENERAL CHAT (LLM)
    async def _handle_general_conversation(self, message: str) -> str:
        try:
            if not self.llm_service:
                return "Chat service is not available."
                
            return await self.llm_service.generate(
                system_prompt=GENERAL_CHAT_PROMPT,
                user_prompt=message,
                
            )

        except Exception as e:
            print(f"LLM error: {e}")
            return "Sorry, I couldn't process your request right now."

  #chat with db saving
    async def chat_with_saving(
        self,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        if not self.conversation_service:
            raise Exception("DB not initialized")

        try:
            user_msg = self.conversation_service.save_message(
                user_id=user_id,
                message_type="user",
                content=message,
                session_id=session_id
            )

            response_text = await self.chat(message, context)

            bot_msg = self.conversation_service.save_message(
                user_id=user_id,
                message_type="bot",
                content=response_text,
                session_id=session_id
            )

            return {
                "user_message": user_msg,
                "bot_message": bot_msg,
                "response": response_text
            }

        except Exception as e:
            print(f"Save chat error: {e}")
            raise e

    # Welcome message
    def save_welcome_message(self, user_id: int, session_id: Optional[str] = None):
        if not self.conversation_service:
            raise Exception("DB not initialized")

        welcome_text = "Hello! I am your Career Assistant. How can I help you today?"

        return self.conversation_service.save_message(
            user_id=user_id,
            message_type="bot",
            content=welcome_text,
            session_id=session_id
        )