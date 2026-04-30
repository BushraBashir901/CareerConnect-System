from sqlalchemy.orm import Session

from app.services.job_search_service import JobSearchService
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMService

from app.services.chatbot_tools.job_search_tool import JobSearchTool
from app.services.chatbot_tools.career_advice_tool import CareerAdviceTool
from app.services.chatbot_tools.interviewpreparation_tool import InterviewPreparationTool
from app.services.chatbot_tools.message_parser import MessageParser
from app.services.chatbot_tools.handlers import ChatbotHandlers


class Container:
    """
    Central Dependency Injection Container
    Prevents circular imports + repeated object creation
    """

    def __init__(self, db: Session):
        self.db = db

        # CORE SERVICES (LOW LEVEL)
        self.job_search_service = JobSearchService(db)
        self.conversation_service = ConversationService(db)
        self.llm_service = LLMService()

        # TOOLS (MIDDLE LAYER)
        self.job_search_tool = JobSearchTool(self.job_search_service)
        self.career_advice_tool = CareerAdviceTool(self.llm_service)
        self.interview_tool = InterviewPreparationTool(self.llm_service)
        self.message_parser = MessageParser()

        # HANDLERS (LOGIC LAYER)
        self.handlers = ChatbotHandlers(
            job_search_tool=self.job_search_tool,
            career_advice_tool=self.career_advice_tool,
            interview_tool=self.interview_tool
        )

    # GETTERS (SAFE ACCESS)
    def get_job_search_tool(self):
        return self.job_search_tool

    def get_handlers(self):
        return self.handlers

    def get_parser(self):
        return self.message_parser

    def get_conversation_service(self):
        return self.conversation_service

    def get_llm_service(self):
        return self.llm_service