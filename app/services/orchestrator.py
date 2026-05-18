import time
import asyncio
from typing import Optional

import tiktoken
from app.core.logger import logger

from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.tools.registry import get_tool_registry
from app.prompts.system import SYSTEM_PROMPT
from app.prompts.tool_formatting import format_tool_prompt

from task.message_batch_worker import save_messages_batch
from task.summarization_worker import summarize_conversation

from app.core.ai.intent_router import IntentRouter, Intent
from app.core.ai.query_router import QueryRouter, Route

from app.core.redis_client import redis_client
from app.services.memory_service import (
    add_message,
    get_recent_messages,
    get_summary,
    messages_key,
)


class ChatbotOrchestrator:
    """
    Main orchestration layer of the chatbot system.

    Responsibilities:
    - Load conversation memory (recent messages + summary)
    - Classify intent and route query (Direct / RAG / Tool)
    - Execute LLM / RAG / Tool pipelines
    - Persist conversation state (Redis + DB via Celery)
    - Trigger summarization when needed
    """

    def __init__(self, llm_service: LLMService):
        """
        Initialize orchestrator with required services.
        """

        self.llm_service = llm_service
        self.tool_registry = get_tool_registry()
        self.system_prompt = SYSTEM_PROMPT
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # ROUTERS
        self.intent_router = IntentRouter()
        self.query_router = QueryRouter()

    async def process_message(
        self,
        request: ChatRequest,
        intent: Optional[Intent] = None,
        confidence: float = 0.0,
    ) -> ChatResponse:
        """
        Main entry point for processing a user message.

        Flow:
        1. Load memory (recent messages + summary)
        2. Detect intent and route request
        3. Execute appropriate pipeline (Direct / RAG / Tool)
        4. Store messages in memory + DB
        5. Trigger summarization if needed
        """

        start_time = time.time()

        recent_messages = get_recent_messages(request.user_id, request.session_id)

        summary = get_summary(request.user_id, request.session_id)

        # INTENT + ROUTING
        intent, confidence = self.intent_router.classify(request.message)

        route = self.query_router.route(intent, confidence)

        # EXECUTION LAYER
        if route == Route.DIRECT:
            result = await self._process_direct_llm(request, recent_messages, summary)

        elif route == Route.RAG:
            result = await self._process_rag(request, recent_messages, summary)

        elif route == Route.TOOL:
            result = await self._process_with_tools(
                request, intent.value, recent_messages, summary
            )

        else:
            result = {"text": "Can you clarify your request?"}

        response_text = result["text"]

        # STORE MEMORY
        add_message(request.user_id, request.session_id, "user", request.message)
        add_message(request.user_id, request.session_id, "assistant", response_text)

        save_messages_batch.delay(
            request.user_id,
            request.session_id,
            [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": response_text},
            ],
        )

        # SUMMARY TRIGGER
        count = redis_client.llen(messages_key(request.user_id, request.session_id))

        if count >= 5 and count % 5 == 0:
            summarize_conversation.delay(request.user_id, request.session_id)

            logger.info("summary_triggered", extra={"count": count})

        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            timestamp=time.time(),
            metadata={
                "processing_time": time.time() - start_time,
                "intent": intent.value,
                "confidence": confidence,
                "route": route.value,
            },
        )

    # DIRECT LLM
    async def _process_direct_llm(self, request, recent_messages, summary):
        """
        Direct LLM response pipeline (no tools, no retrieval).
        """

        prompt = self._build_prompt(request.message, recent_messages, summary)

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt, user_prompt=prompt
        )

        return {"text": response}

    # RAG PIPELINE
    async def _process_rag(self, request, recent_messages, summary):
        """
        RAG pipeline (retrieval augmented generation).
        Currently placeholder for vector DB integration.
        """

        # TODO: connect vector DB here
        context = ""

        prompt = f"""
Context:
{context}

User Question:
{request.message}
"""

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt, user_prompt=prompt
        )

        return {"text": response}

    # TOOL EXECUTION
    async def _process_with_tools(self, request, tool_name, recent_messages, summary):
        """
        Tool execution pipeline.

        - Fetch tool from registry
        - Execute tool
        - Pass result back to LLM for final response
        """

        tool = self.tool_registry.get_tool(tool_name)

        if not tool:
            return await self._process_direct_llm(request, recent_messages, summary)

        tool_result = await tool.execute(
            {
                "tool_name": tool_name,
                "parameters": {"query": request.message},
                "user_id": request.user_id,
                "session_id": request.session_id,
            }
        )

        if not tool_result.success:
            return await self._process_direct_llm(request, recent_messages, summary)

        prompt = format_tool_prompt(tool_result.result, request.message, summary or "")

        response = await self.llm_service.generate(
            system_prompt=self.system_prompt, user_prompt=prompt
        )

        return {"text": response}

    # PROMPT BUILDER
    def _build_prompt(self, message, recent_messages, summary):
        """
        Build final prompt from memory + user input.
        """
        prompt = "You are an AI assistant.\n\n"

        if summary:
            prompt += f"Summary:\n{summary}\n\n"

        if recent_messages:
            prompt += "Recent Messages:\n"
            prompt += "\n".join(recent_messages[-3:])

        prompt += f"\nUser: {message}\n"

        return prompt


# SINGLETON
_global_orchestrator = None
_orchestrator_lock = asyncio.Lock()


async def get_global_orchestrator():
    global _global_orchestrator

    async with _orchestrator_lock:
        if _global_orchestrator is None:
            _global_orchestrator = ChatbotOrchestrator(llm_service=LLMService())

    return _global_orchestrator
