from app.core.llm_client import client
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.job_search_service import JobSearchService
from app.services.chatbot_tools.job_search_tool import JobSearchTool
from app.services.chatbot_tools.career_advice_tool import CareerAdviceTool, InterviewPreparationTool
from app.services.chatbot_tools.message_parser import MessageParser
from app.services.chatbot_tools.handlers import ChatbotHandlers
from app.services.chatbot_tools.prompts import GENERAL_CHAT_PROMPT
from app.services.conversation_service import ConversationService


class CareerConnectChatbot:
    """
    AI-powered career assistant chatbot using DeepSeek API.
    
    Provides intelligent career guidance, job search assistance, interview preparation,
    and skill development advice through natural language conversations.
    
    Attributes:
        job_search_tool: Tool for handling job search queries
        career_advice_tool: Tool for providing career guidance
        interview_tool: Tool for interview preparation assistance
        message_parser: Tool for categorizing and parsing user messages
        handlers: Coordinator for handling different message types
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize CareerConnect chatbot.
        
        Args:
            db: Optional database session for job search functionality
            
        Note:
            - Uses OpenAI API for AI responses
            - Initializes specialized tools for different query types
            - Job search functionality requires database session
        """
        self.db = db
        self.conversation_service = ConversationService(db) if db else None
        
        print("Using OpenAI API for AI responses")
        
        # Initialize OpenAI client for general conversation
        self.client = client
        
        # Initialize job search service if database session is provided
        job_search_service = JobSearchService(db) if db else None

        self.job_search_tool = JobSearchTool(job_search_service) if job_search_service else None
        self.career_advice_tool = CareerAdviceTool()
        self.interview_tool = InterviewPreparationTool()
        self.message_parser = MessageParser()

        self.handlers = ChatbotHandlers(
            job_search_tool=self.job_search_tool,
            career_advice_tool=self.career_advice_tool,
            interview_tool=self.interview_tool
        )

    async def chat(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process user message and generate appropriate response.
        
        Categorizes the message and routes it to the appropriate handler
        based on the detected intent (job search, career advice, interview prep, etc.).
        
        Args:
            message: User's input message
            context: Optional context information for the conversation
            
        Returns:
            str: Generated response from the appropriate handler
            
        Raises:
            Exception: If message processing fails (returns error message)
        """
        try:
            category, extracted_info = self.message_parser.categorize_message(message)

            if category == "job_search" and self.job_search_tool:
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
            print(f"Error in chat processing: {e}")
            return "Sorry, I encountered an error processing your message. Please try again."


    async def _handle_general_conversation(self, message: str) -> str:
        """
        Handle general conversation queries using OpenAI API.
        
        Used for messages that don't fit into specialized categories
        like job search or career advice.
        
        Args:
            message: User's general conversation message
            
        Returns:
            str: AI-generated response for general conversation
        
        Raises:
            Exception: If API fails to generate response (returns error message)
        """
        try:
            messages = [
                {"role": "system", "content": GENERAL_CHAT_PROMPT},
                {"role": "user", "content": message}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return (
                "Sorry, I encountered an error while processing "
                "your request. Please try again."
            )
    
    async def chat_with_saving(self, 
                            user_id: int, 
                            message: str, 
                            session_id: Optional[str] = None,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message, generate response, and save both to database.
        
        This method handles the complete chat flow including message persistence.
        
        Args:
            user_id: ID of the user sending the message
            message: User's input message
            session_id: Optional session ID to group messages
            context: Optional context information for the conversation
            
        Returns:
            Dict containing:
                - user_message: The saved user message record
                - bot_response: The saved bot message record
                - response_text: The bot's response text
                
        Raises:
            Exception: If message processing or saving fails
        """
        if not self.conversation_service:
            raise Exception("Conversation service not available")
        
        try:
            # Save user message
            user_message = self.conversation_service.save_message(
                user_id=user_id,
                message_type='user',
                content=message,
                session_id=session_id
            )
            
            # Generate bot response
            response_text = await self._handle_general_conversation(message)
            
            # Save bot response
            bot_message = self.conversation_service.save_message(
                user_id=user_id,
                message_type='bot',
                content=response_text,
                session_id=session_id
            )
            
            return {
                "user_message": user_message,
                "bot_response": bot_message,
                "response_text": response_text
            }
            
        except Exception as e:
            print(f"Error in chat with saving: {e}")
            # Save error message
            error_message = "Sorry, I encountered an error processing your message. Please try again."
            self.conversation_service.save_message(
                user_id=user_id,
                message_type='system',
                content=error_message,
                session_id=session_id
            )
            raise e
    
    def save_welcome_message(self, user_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Save welcome message to database.
        
        Args:
            user_id: ID of the user
            session_id: Optional session ID to group messages
            
        Returns:
            Dict containing the saved welcome message and its text
        """
        if not self.conversation_service:
            raise Exception("Conversation service not available")
        
        welcome_text = "Hello! I'm your CareerConnect AI assistant. How can I help you with your career today?"
        
        welcome_message = self.conversation_service.save_message(
            user_id=user_id,
            message_type='bot',
            content=welcome_text,
            session_id=session_id
        )
        
        return {
            "welcome_message": welcome_message,
            "welcome_text": welcome_text
        }