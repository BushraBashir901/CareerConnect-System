"""
Chatbot Orchestrator (Production-Ready Step 03)
- Redis memory (recent messages + summary)
- Tool routing
- LLM processing
- Background summarization trigger
"""

import time
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.tools.registry import get_tool_registry
from app.repositories.chatbot_repo.conversation_repo import ConversationRepository
from app.db.session import SessionLocal

from app.core.logger import logger
from app.prompts.system import SYSTEM_PROMPT
from app.prompts.tool_formatting import format_tool_prompt
from task.summarization_worker import summarize_conversation


from app.services.memory_service import (
    add_message,
    get_recent_messages,
    get_summary,
    should_summarize,
    reset_memory,
    set_summary
)


# MODE ENUM
class ProcessingMode(Enum):
    DIRECT_LLM = "direct_llm"
    TOOL_EXECUTION = "tool_execution"

# ORCHESTRATOR
class ChatbotOrchestrator:

    def __init__(self, llm_service: LLMService, conversation_repo: ConversationRepository):
        self.llm_service = llm_service
        self.conversation_repo = conversation_repo
        self.tool_registry = get_tool_registry()
        self.system_prompt = SYSTEM_PROMPT

    
# MAIN ENTRY
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()

        logger.info("message_processing_start", extra={
            "user_id": request.user_id,
            "session_id": request.session_id
        })

        try:
            # 1. STORE USER MESSAGE (Redis)
            add_message(request.session_id, "user", request.message)

            # 2. FETCH CONTEXT (Redis)
            recent_messages = get_recent_messages(request.session_id)
            summary = get_summary(request.session_id)

            
            # 3. ROUTING (tool vs LLM)
            mode, tool_name = await self._determine_processing_mode_and_tool(
                request.message
            )

            if mode == ProcessingMode.TOOL_EXECUTION:
                result = await self._process_with_tools(
                    request, tool_name, recent_messages, summary
                )
            else:
                result = await self._process_direct_llm(
                    request, recent_messages, summary
                )

          
            # 4. STORE ASSISTANT MESSAGE (Redis)
            add_message(request.session_id, "assistant", result["text"])

          
            # 5. TRIGGER SUMMARIZATION (async)
            if should_summarize(request.session_id):
                summarize_conversation.delay(session_id=request.session_id)

           
            # 6. RESPONSE
            return ChatResponse(
                response=result["text"],
                session_id=request.session_id,
                timestamp=time.time(),
                metadata={
                    "processing_time": time.time() - start_time,
                    "mode": mode.value,
                    "tools_used": result.get("tools_used", [])
                }
            )

        except Exception as e:
            logger.error("chat_error", extra={"error": str(e)})

            return ChatResponse(
                response="Sorry, I encountered an error while processing your request.",
                session_id=request.session_id,
                timestamp=time.time(),
                metadata={"error": str(e)}
            )


# ROUTING LOGIC
    async def _determine_processing_mode_and_tool(
        self, message: str
    ) -> tuple[ProcessingMode, Optional[str]]:

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
    
# TOOL PIPELINE
    async def _process_with_tools(
        self,
        request: ChatRequest,
        tool_name: Optional[str],
        recent_messages,
        summary
    ) -> Dict[str, Any]:

        if not tool_name:
            return await self._process_direct_llm(request, recent_messages, summary)

        tool = self.tool_registry.get_tool(tool_name)

        if not tool:
            return await self._process_direct_llm(request, recent_messages, summary)

        params = await self._extract_tool_parameters(request.message, tool)

        tool_response = await tool.execute({
            "tool_name": tool_name,
            "parameters": params,
            "user_id": request.user_id,
            "session_id": request.session_id
        })

        if not tool_response.success:
            return await self._process_direct_llm(request, recent_messages, summary)

        prompt = format_tool_prompt(
            tool_response.result,
            request.message,
            summary or ""
        )

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt
        )

        return {
            "text": response,
            "tools_used": [tool_name]
        }

    # =========================================================
    # DIRECT LLM PIPELINE
    # =========================================================
    async def _process_direct_llm(
        self,
        request: ChatRequest,
        recent_messages,
        summary
    ) -> Dict[str, Any]:

        prompt = self._build_prompt(
            request.message,
            recent_messages,
            summary
        )

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt
        )

        return {
            "text": response,
            "tools_used": []
        }

    # =========================================================
    # PROMPT BUILDER
    # =========================================================
    def _build_prompt(self, message, recent_messages, summary):

        prompt = "You are an AI assistant.\n\n"

        if summary:
            prompt += f"Conversation Summary:\n{summary}\n\n"

        if recent_messages:
            prompt += "Recent Conversation:\n"
            for msg in recent_messages:
                prompt += f"{msg}\n"

        prompt += f"\nUser Message:\n{message}"

        return prompt

    # =========================================================
    # TOOL PARAM EXTRACTION
    # =========================================================
    async def _extract_tool_parameters(self, message: str, tool) -> Dict[str, Any]:

        if tool.name == "job_search":
            return {"query": message}

        if tool.name == "career_advice":
            return {"topic": message}

        return {}

    # =========================================================
    # SUMMARIZATION WORKER (ASYNC)
    # =========================================================
    async def _trigger_summarization(self, session_id: str):

        try:
            messages = get_recent_messages(session_id)

            summary = await self.llm_service.generate(
                system_prompt="Summarize this conversation briefly.",
                user_prompt=str(messages)
            )

            set_summary(session_id, summary)
            reset_memory(session_id)

            logger.info("conversation_summarized", extra={
                "session_id": session_id
            })

        except Exception as e:
            logger.error("summarization_error", extra={
                "session_id": session_id,
                "error": str(e)
            })


# =========================================================
# SINGLETON ORCHESTRATOR
# =========================================================
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