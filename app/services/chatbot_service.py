from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from app.core.config import settings
from app.services.job_search_service import JobSearchService
from app.services.chatbot_tools.job_search_tool import JobSearchTool
from app.services.chatbot_tools.career_advice_tool import CareerAdviceTool, InterviewPreparationTool
from app.services.chatbot_tools.message_parser import MessageParser
from app.services.chatbot_tools.handlers import ChatbotHandlers
from app.services.chatbot_tools.prompts import GENERAL_CHAT_PROMPT


class CareerConnectChatbot:
    """
    AI-powered career assistant chatbot using PydanticAI and Ollama.
    
    Provides intelligent career guidance, job search assistance, interview preparation,
    and skill development advice through natural language conversations.
    
    Attributes:
        model: Ollama language model for generating responses
        job_search_tool: Tool for handling job search queries
        career_advice_tool: Tool for providing career guidance
        interview_tool: Tool for interview preparation assistance
        message_parser: Tool for categorizing and parsing user messages
        handlers: Coordinator for handling different message types
        agent: General conversation agent for non-specialized queries
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the CareerConnect chatbot.
        
        Args:
            db: Optional database session for job search functionality
            
        Note:
            - Uses Ollama model from settings or defaults to gemma2:2b
            - Initializes specialized tools for different query types
            - Job search functionality requires database session
        """

        ollama_url = getattr(settings, "OLLAMA_URL", "http://localhost:11434/v1")

        model_name = getattr(settings, "OLLAMA_MODEL", "gemma2:2b")

        print("Using Ollama model:", model_name)
        print("Ollama URL:", ollama_url)

        provider = OllamaProvider(base_url=ollama_url)

        self.model = OllamaModel(
            model_name=model_name,
            provider=provider
        )

        job_search_service = JobSearchService(db) if db else None

        self.job_search_tool = JobSearchTool(job_search_service) if job_search_service else None
        self.career_advice_tool = CareerAdviceTool(self.model)
        self.interview_tool = InterviewPreparationTool(self.model)
        self.message_parser = MessageParser()

        self.handlers = ChatbotHandlers(
            job_search_tool=self.job_search_tool,
            career_advice_tool=self.career_advice_tool,
            interview_tool=self.interview_tool
        )

        self.agent = Agent(
            model=self.model,
            system_prompt=GENERAL_CHAT_PROMPT
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
            return f"Error: {str(e)}"

    async def _handle_general_conversation(self, message: str) -> str:
        """
        Handle general conversation queries using the base AI agent.
        
        Used for messages that don't fit into specialized categories
        like job search or career advice.
        
        Args:
            message: User's general conversation message
            
        Returns:
            str: AI-generated response for general conversation
            
        Raises:
            Exception: If agent fails to generate response (returns error message)
        """
        try:
            result = await self.agent.run(message)
            return result.output
        except Exception as e:
            return f"Error: {str(e)}"