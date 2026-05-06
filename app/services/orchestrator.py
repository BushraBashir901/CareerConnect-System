"""
Chatbot orchestrator service for coordinating all chatbot components.
"""

import time
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

from app.schemas.conversation import ChatRequest, ChatResponse
from app.schemas.rag import RetrievalRequest
from app.services.llm_service import LLMService
from app.services.retriever_service import RetrieverService
from app.services.memory_manager import MemoryManager
from app.tools.registry import get_tool_registry
from app.repositories.chatbot_repo.conversation_repo import ConversationRepository

from app.db.session import SessionLocal
from app.core.logger import logger

from app.prompts.system import SYSTEM_PROMPT
from app.prompts.tool_formatting import format_tool_prompt


class ProcessingMode(Enum):
    DIRECT_LLM = "direct_llm"
    TOOL_EXECUTION = "tool_execution"


class ChatbotOrchestrator:

    def __init__(self, llm_service: LLMService, conversation_repo: ConversationRepository):
        self.llm_service = llm_service
        self.conversation_repo = conversation_repo
        self.tool_registry = get_tool_registry()
        self.retriever_service = RetrieverService()
        self.memory_manager = MemoryManager()

        self.system_prompt = SYSTEM_PROMPT

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()

        logger.info("message_processing_start", extra={
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message": request.message
        })

        try:
            # Save user message
            self.conversation_repo.save_message(
                user_id=request.user_id,
                message_type="user",
                content=request.message,
                session_id=request.session_id
            )

            # Decide mode + tool
            mode, tool_name = await self._determine_processing_mode_and_tool(request.message)

            logger.info("processing_mode_selected", extra={
                "mode": mode.value,
                "tool": tool_name
            })

            # Execute pipeline
            if mode == ProcessingMode.TOOL_EXECUTION:
                result = await self._process_with_tools(request, tool_name)
            else:
                result = await self._process_direct_llm(request)

            # Save assistant message
            self.conversation_repo.save_message(
                user_id=request.user_id,
                message_type="assistant",
                content=result["text"],
                session_id=request.session_id
            )

            processing_time = time.time() - start_time

            return ChatResponse(
                response=result["text"],
                session_id=request.session_id or "default",
                timestamp=time.time(),
                metadata={
                    "processing_mode": mode.value,
                    "processing_time": processing_time,
                    "tools_used": result.get("tools_used", [])
                }
            )

        except Exception as e:
            logger.error("chat_error", extra={"error": str(e)})

            return ChatResponse(
                response="I encountered an error while processing your request.",
                session_id=request.session_id or "default",
                timestamp=time.time(),
                metadata={"error": str(e)}
            )

    # ---------------------------
    # ROUTING LOGIC
    # ---------------------------

    async def _determine_processing_mode_and_tool(self, message: str) -> tuple[ProcessingMode, Optional[str]]:

        msg = message.lower()

        tool_map = {
            "career_advice": ["career", "advice", "guidance"],
            "job_search": ["job", "search", "find job"],
            "interview_preparation": ["interview", "prepare"],
            "skill_development": ["skill", "learn", "develop"]
        }

        for tool, keywords in tool_map.items():
            if any(k in msg for k in keywords):
                return ProcessingMode.TOOL_EXECUTION, tool

        return ProcessingMode.DIRECT_LLM, None

    # ---------------------------
    # TOOL EXECUTION
    # ---------------------------

    async def _process_with_tools(self, request: ChatRequest, tool_name: Optional[str]) -> Dict[str, Any]:

        if not tool_name:
            return await self._process_direct_llm(request)

        tool = self.tool_registry.get_tool(tool_name)

        if not tool:
            return await self._process_direct_llm(request)

        parameters = await self._extract_tool_parameters(request.message, tool)

        tool_response = await tool.execute({
            "tool_name": tool_name,
            "parameters": parameters,
            "user_id": request.user_id,
            "session_id": request.session_id
        })

        if not tool_response.success:
            return await self._process_direct_llm(request)

        
        prompt = format_tool_prompt(
            tool_response.result,
            request.message,
            ""
        )

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt
        )

        return {
            "text": response,
            "tools_used": [tool_name]
        }

    # ---------------------------
    # DIRECT LLM
    # ---------------------------

    async def _process_direct_llm(self, request: ChatRequest) -> Dict[str, Any]:

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=request.message
        )

        return {
            "text": response,
            "tools_used": []
        }

    # ---------------------------
    # TOOL PARAM EXTRACTION
    # ---------------------------

    async def _extract_tool_parameters(self, message: str, tool) -> Dict[str, Any]:

        msg = message.lower()
        params = {}

        if tool.name == "job_search":
            params["query"] = message

        elif tool.name == "career_advice":
            params["topic"] = message

        return params

    # ---------------------------
    # STATS
    # ---------------------------

    def get_stats(self) -> Dict[str, Any]:
        return {
            "tools": self.tool_registry.get_tool_names(),
            "memory": self.memory_manager.get_stats()
        }


# ---------------------------
# SINGLETON
# ---------------------------

_global_orchestrator = None
_orchestrator_lock = asyncio.Lock()


async def get_global_orchestrator():
    global _global_orchestrator

    async with _orchestrator_lock:
        if _global_orchestrator is None:

            db = SessionLocal()
            repo = ConversationRepository(db)

            _global_orchestrator = ChatbotOrchestrator(
                llm_service=LLMService(),
                conversation_repo=repo
            )

    return _global_orchestrator