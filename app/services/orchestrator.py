import time
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

from app.core import redis_client
from app.schemas.conversation import ChatRequest, ChatResponse
from app.services import memory_service
from app.services.llm_service import LLMService
from app.tools.registry import get_tool_registry
from task.message_batch_worker import save_messages_batch

from app.core.logger import logger
from app.prompts.system import SYSTEM_PROMPT
from app.prompts.tool_formatting import format_tool_prompt

from app.services.memory_service import (
    add_message,
    get_recent_messages,
    get_message_count,
    get_summary,
    set_summary,
    create_session,
    update_summary,
)


class ProcessingMode(Enum):
    DIRECT_LLM = "direct_llm"
    TOOL_EXECUTION = "tool_execution"

class ChatbotOrchestrator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.tool_registry = get_tool_registry()
        self.system_prompt = SYSTEM_PROMPT


    async def process_message(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()

        logger.info(
            "message_processing_start",
            extra={
                "user_id": request.user_id,
                "session_id": request.session_id,
            },
        )

        try:
            create_session(request.user_id, request.session_id)

            add_message(
                request.user_id,
                request.session_id,
                "user",
                request.message,
            )

            recent_messages = get_recent_messages(
                request.user_id,
                request.session_id,
            )

            summary = get_summary(
                request.user_id,
                request.session_id,
            )

            mode, tool_name = await self._determine_processing_mode_and_tool(
                request.message
            )

            tool_result = None

            if mode == ProcessingMode.TOOL_EXECUTION:
                tool_result = await self._process_with_tools(request, tool_name, recent_messages, summary)
                response_text = tool_result["text"]
            else:
                result = await self._process_direct_llm(request, recent_messages, summary)
                response_text = result["text"]

            add_message(
                request.user_id,
                request.session_id,
                "assistant",
                response_text,
            )


            save_messages_batch.delay(
                request.user_id,
                request.session_id,
                [
                    {
                        "role": "user",
                        "content": request.message,
                    },
                    {
                        "role": "assistant",
                        "content": response_text,
                    },
                ],
            )
            message_count = get_message_count(request.user_id, request.session_id)
            if message_count % 5 == 0:
                recent_messages = get_recent_messages(request.user_id, request.session_id)
                old_summary = get_summary(request.user_id, request.session_id)

                new_summary = await update_summary(
                    self.llm_service,
                    old_summary,
                    recent_messages
                )

                set_summary(request.user_id, request.session_id, new_summary)
            
            return ChatResponse(
                response=response_text,
                session_id=request.session_id,
                timestamp=time.time(),
                metadata={
                    "processing_time": time.time() - start_time,
                    "mode": mode.value,
                    "tool_used": tool_name,
                },
            )

        except Exception as e:
            logger.error("chat_error", extra={"error": str(e)})

            return ChatResponse(
                response="Sorry, I encountered an error while processing your request.",
                session_id=request.session_id,
                timestamp=time.time(),
                metadata={"error": str(e)},
            )

    async def _determine_processing_mode_and_tool(
        self, message: str
    ) -> tuple[ProcessingMode, Optional[str]]:

        msg = message.lower()

        tool_map = {
            "career_advice": ["career", "advice", "guidance"],
            "job_search": ["job", "search", "find job"],
            "interview_preparation": ["interview", "prepare"],
            "skill_development": ["skill", "learn", "develop"],
        }

        for tool, keywords in tool_map.items():
            if any(k in msg for k in keywords):
                logger.info("tool_selected", extra={"tool": tool, "message": message})
                return ProcessingMode.TOOL_EXECUTION, tool

        logger.info("direct_llm_selected", extra={"message": message})
        return ProcessingMode.DIRECT_LLM, None

    async def _process_with_tools(
        self, request: ChatRequest, tool_name: Optional[str], recent_messages, summary
    ) -> Dict[str, Any]:

        if not tool_name:
            return await self._process_direct_llm(request, recent_messages, summary)

        tool = self.tool_registry.get_tool(tool_name)

        if not tool:
            logger.warning("tool_not_found", extra={"tool_name": tool_name})
            return await self._process_direct_llm(request, recent_messages, summary)

        params = await self._extract_tool_parameters(request.message, tool)

        logger.info("tool_execution_start", extra={"tool_name": tool_name, "params": params})
        tool_start_time = time.time()
        tool_response = await tool.execute(
            {
                "tool_name": tool_name,
                "parameters": params,
                "user_id": request.user_id,
                "session_id": request.session_id,
            }
        )
        tool_execution_time = time.time() - tool_start_time
        logger.info("tool_execution_complete", extra={"tool_name": tool_name, "execution_time": tool_execution_time})

        if not tool_response.success:
            return await self._process_direct_llm(request, recent_messages, summary)

        prompt = format_tool_prompt(
            tool_response.result, request.message, summary or ""
        )

        llm_start_time = time.time()
        response = await self.llm_service.generate(
            system_prompt=self.system_prompt, user_prompt=prompt
        )
        llm_execution_time = time.time() - llm_start_time
        logger.info("llm_execution_complete", extra={"execution_time": llm_execution_time, "pipeline": "tool"})

        return {"text": response, "tools_used": [tool_name]}

    
    async def _process_direct_llm(
        self, request: ChatRequest, recent_messages, summary
    ) -> Dict[str, Any]:

        prompt = self._build_prompt(request.message, recent_messages, summary)

        full_response = await self.llm_service.generate(
            system_prompt=self.system_prompt, user_prompt=prompt
        )

        if "SUMMARY:" in full_response:
            parts = full_response.split("SUMMARY:", 1)
            user_response = parts[0].strip()
            new_summary = parts[1].strip()
        else:
            user_response = full_response.strip()
            new_summary = summary or ""

        set_summary(request.user_id, request.session_id, new_summary)

        return {"text": user_response, "tools_used": []}

  
    def _build_prompt(self, message, recent_messages, summary):

        prompt = "You are an AI assistant.\n\n"

        if summary:
            prompt += f"Conversation Summary:\n{summary}\n\n"

        if recent_messages:
            prompt += "Recent Conversation:\n"
            for msg in recent_messages:
                prompt += f"{msg}\n"

        prompt += f"\nUser Message:\n{message}\n\n"

        prompt += "Respond clearly and update SUMMARY at the end."

        return prompt

    
    async def _extract_tool_parameters(self, message: str, tool) -> Dict[str, Any]:

        if tool.name == "job_search":
            return {"query": message}

        if tool.name == "career_advice":
            return {"topic": message}

        return {}
   
    def _save_message(self, repo, user_id, message_type, content, session_id):
        repo.save_message(
            user_id=user_id,
            message_type=message_type,
            content=content,
            session_id=session_id,
        
        )
        
    async def build_context(user_id, session_id):
        summary = redis_client.get(f"summary:user:{user_id}")

 
        recent_messages = await memory_service.get_recent_messages(session_id)
        messages = []

        messages.append({
            "role": "system",
            "content": f"Previous conversation summary:\n{summary}"
        })
        messages.extend(recent_messages)

        return messages



_global_orchestrator = None
_orchestrator_lock = asyncio.Lock()


async def get_global_orchestrator():
    global _global_orchestrator

    async with _orchestrator_lock:
        if _global_orchestrator is None:
            _global_orchestrator = ChatbotOrchestrator(llm_service=LLMService())

    return _global_orchestrator

