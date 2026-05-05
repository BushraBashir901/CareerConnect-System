"""
Chatbot orchestrator service for coordinating all chatbot components.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum

from app.schemas.conversation import ChatRequest, ChatResponse
from app.schemas.rag import RetrievalRequest
from app.services.llm_service import LLMService
from app.services.retriever_service import RetrieverService
from app.services.memory_manager import MemoryManager
from app.tools.registry import get_tool_registry
from app.repositories.message_repository import MessageRepository
from app.models.chatbot_message import ChatMessage
from app.db.session import SessionLocal
from app.core.logger import logger


class ProcessingMode(Enum):
    """Processing modes for chatbot responses."""
    DIRECT_LLM = "direct_llm"
    TOOL_EXECUTION = "tool_execution"


class ChatbotOrchestrator:
    """Simplified orchestrator for career advice chatbot."""
    
    def __init__(self, llm_service: LLMService, message_repo: MessageRepository):
        self.llm_service = llm_service
        self.message_repo = message_repo
        self.tool_registry = get_tool_registry()
        self.retriever_service = RetrieverService()
        self.memory_manager = MemoryManager()
        self.system_prompt = self._get_system_prompt()
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and generate response."""
        start_time = time.time()
        logger.info("message_processing_start", 
                   extra={
                       "user_id": request.user_id,
                       "session_id": request.session_id,
                       "message": request.message
                   })
        
        try:
            # Get conversation history from database
            history = await self.message_repo.get_history(request.session_id)
            logger.info("history_retrieved", 
                       extra={
                           "user_id": request.user_id,
                           "session_id": request.session_id,
                           "history_count": len(history)
                       })
            
            # Save user message to database
            await self.message_repo.save_message(
                request.session_id, "user", request.message, request.user_id
            )
            
            # Determine processing mode and tool in one pass
            processing_mode, selected_tool = await self._determine_processing_mode_and_tool(request.message)
            logger.info("processing_mode_selected", 
                   extra={
                       "user_id": request.user_id,
                       "session_id": request.session_id,
                       "processing_mode": processing_mode.value,
                       "selected_tool": selected_tool
                   })
            
            # Process based on mode
            if processing_mode == ProcessingMode.TOOL_EXECUTION:
                logger.info("tool_execution_start", 
                       extra={
                           "user_id": request.user_id,
                           "session_id": request.session_id,
                           "selected_tool": selected_tool
                       })
                response = await self._process_with_tools(request, selected_tool)
            else:
                logger.info("direct_llm_processing", 
                           extra={
                               "user_id": request.user_id,
                               "session_id": request.session_id
                           })
                response = await self._process_direct_llm(request, history)
            
            # Save assistant response to database
            await self.message_repo.save_message(
                request.session_id, "assistant", response["text"], request.user_id
            )
            
            processing_time = time.time() - start_time
            logger.info("response_generated", 
                       extra={
                           "user_id": request.user_id,
                           "session_id": request.session_id,
                           "processing_time": round(processing_time, 2),
                           "tools_used": response.get('tools_used', [])
                       })
            
            return ChatResponse(
                response=response["text"],
                session_id=request.session_id or "default",
                timestamp=time.time(),
                metadata={
                    "processing_mode": processing_mode.value,
                    "processing_time": processing_time,
                    "tools_used": response.get("tools_used", [])
                }
            )
            
        except Exception as e:
            return ChatResponse(
                response=f"I apologize, but I encountered an error: {str(e)}",
                session_id=request.session_id or "default",
                timestamp=time.time(),
                metadata={"error": str(e)}
            )
    
    async def _determine_processing_mode_and_tool(self, message: str) -> tuple[ProcessingMode, Optional[str]]:
        """Determine processing mode and tool in one pass."""
        
        message_lower = message.lower()
        
        # Tool mapping with keywords - single source of truth
        tool_keywords_map = {
            "career_advice": ["career", "advice", "guidance"],
            "job_search": ["job", "search", "find job"],
            "interview_preparation": ["interview", "prepare", "questions"],
            "skill_development": ["skill", "learn", "develop"]
        }
        
        # Additional keywords for tool execution mode
        additional_tool_keywords = ["search", "find", "look for", "recommend", "help me", "calculate", "what is"]
        
        # Single pass to find matching tool
        selected_tool = None
        for tool_name, keywords in tool_keywords_map.items():
            if any(keyword in message_lower for keyword in keywords):
                selected_tool = tool_name
                break
        
        # Check if any tool-related keywords are present
        all_tool_keywords = []
        for keywords in tool_keywords_map.values():
            all_tool_keywords.extend(keywords)
        all_tool_keywords.extend(additional_tool_keywords)
        
        if any(keyword in message_lower for keyword in all_tool_keywords):
            return ProcessingMode.TOOL_EXECUTION, selected_tool
        
        # Default to direct LLM
        return ProcessingMode.DIRECT_LLM, None
    
    async def _process_with_tools(self, request: ChatRequest, selected_tool: Optional[str] = None) -> Dict[str, Any]:
        """Process message using tool execution."""
        
        # Use pre-selected tool, or select if not provided
        tool_name = selected_tool or await self._select_tool(request.message)
        logger.info("final_tool_selection", 
                   extra={
                       "user_id": request.user_id,
                       "session_id": request.session_id,
                       "selected_tool": tool_name
                   })
        
        if not tool_name:
            logger.info("no_tool_selected", 
                       extra={
                           "user_id": request.user_id,
                           "session_id": request.session_id,
                           "fallback": "direct_llm"
                       })
            return await self._process_direct_llm(request, [])
        
        # Execute tool
        try:
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                logger.error("tool_not_found", 
                            extra={
                                "user_id": request.user_id,
                                "session_id": request.session_id,
                                "tool_name": tool_name,
                                "error": "Tool not found in registry"
                            })
                return await self._process_direct_llm(request, [])
            
            # Extract parameters from message
            parameters = await self._extract_tool_parameters(request.message, tool)
            logger.info("tool_parameters_extracted", 
                        extra={
                            "user_id": request.user_id,
                            "session_id": request.session_id,
                            "tool_name": tool_name,
                            "parameters": parameters
                        })
            
            # Execute tool
            logger.info("tool_execution_start", 
                       extra={
                           "user_id": request.user_id,
                           "session_id": request.session_id,
                           "tool_name": tool_name
                       })
            tool_response = await tool.execute({
                "tool_name": tool_name,
                "parameters": parameters,
                "user_id": request.user_id,
                "session_id": request.session_id
            })
            
            if tool_response.success:
                logger.info("tool_execution_success", 
                           extra={
                               "user_id": request.user_id,
                               "session_id": request.session_id,
                               "tool_name": tool_name,
                               "result_length": len(str(tool_response.result))
                           })
                
                # Format tool response
                formatted_response = await self._format_tool_response(
                    tool_response.result, request.message, ""
                )
                
                return {
                    "text": formatted_response,
                    "tools_used": [tool_name],
                    "sources": []
                }
            else:
                logger.error("tool_execution_failed", 
                            extra={
                                "user_id": request.user_id,
                                "session_id": request.session_id,
                                "tool_name": tool_name,
                                "error": tool_response.error
                            })
                # Tool failed, fallback to LLM
                return await self._process_direct_llm(request, [])
                
        except Exception as e:
            logger.error("tool_execution_exception", 
                        extra={
                            "user_id": request.user_id,
                            "session_id": request.session_id,
                            "tool_name": tool_name,
                            "error": str(e)
                        })
            return await self._process_direct_llm(request, [])
    
    async def _process_with_rag(self, request: ChatRequest, context: str) -> Dict[str, Any]:
        """Process message with RAG enhancement."""
        
        if not self.retriever_service:
            return await self._process_direct_llm(request, [])
        
        try:
            # Retrieve relevant documents
            retrieval_request = RetrievalRequest(
                query=request.message,
                context=request.context,
                user_id=request.user_id
            )
            
            retrieval_response = await self.retriever_service.retrieve_context(retrieval_request)
            
            # Build enhanced prompt
            enhanced_prompt = f"""
Context from relevant information:
{retrieval_response.context_text}

User Question: {request.message}

Conversation History:
{context}

Please answer the user's question based on the provided context and conversation history. If the context doesn't contain relevant information, say so and provide a helpful general response.
"""
            
            # Generate response
            response = await self.llm_service.generate(
                system_prompt=self.system_prompt,
                user_prompt=enhanced_prompt
            )
            
            return {
                "text": response,
                "tools_used": [],
                "sources": retrieval_response.retrieved_documents
            }
            
        except Exception as e:
            logger.error("rag_processing_failed", 
                        extra={
                            "user_id": request.user_id,
                            "session_id": request.session_id,
                            "error": str(e)
                        })
            return await self._process_direct_llm(request, [])
    
        
    async def _process_direct_llm(self, request: ChatRequest, history: List[Dict]) -> Dict[str, Any]:
        """Process message using direct LLM."""
        
        response = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=request.message
        )
        
        return {
            "text": response,
            "tools_used": [],
            "sources": []
        }
    
    async def _select_tool(self, message: str) -> Optional[str]:
        """Select the appropriate tool for the message."""
        
        # Simple keyword-based tool selection
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["job", "search", "find job", "looking for"]):
            return "job_search"
        elif any(keyword in message_lower for keyword in ["career", "advice", "guidance"]):
            return "career_advice"
        elif any(keyword in message_lower for keyword in ["interview", "prepare", "questions"]):
            return "interview_preparation"
        elif any(keyword in message_lower for keyword in ["skill", "learn", "develop"]):
            return "skill_development"
        
        return None
    
    async def _extract_tool_parameters(self, message: str, tool) -> Dict[str, Any]:
        """Extract parameters for tool execution."""
        
        # Simple parameter extraction - could be enhanced with NLP
        parameters = {}
        
        if tool.name == "job_search":
            # Extract job search terms
            words = message.split()
            if "in" in words:
                idx = words.index("in")
                if idx + 1 < len(words):
                    parameters["location"] = words[idx + 1]
            
            # Extract query (everything except location)
            query_words = [w for w in words if w.lower() not in ["in", "for", "find", "search"]]
            parameters["query"] = " ".join(query_words)
            
        elif tool.name == "career_advice":
            # Extract field and experience level
            if "as" in message.lower():
                parts = message.lower().split("as")
                if len(parts) > 1:
                    parameters["field"] = parts[1].strip()
        
        return parameters
    
    async def _format_tool_response(self, tool_result: str, 
                                   original_message: str, 
                                   context: str) -> str:
        """Format tool response into natural chat response."""
        
        prompt = f"""
Tool Result:
{tool_result}

Original User Message: {original_message}

Conversation Context: {context}

Please format the tool result into a natural, helpful response to the user's question. Don't just repeat the raw tool output - make it conversational and useful.
"""
        
        return await self.llm_service.generate(
            system_prompt="You are a helpful assistant that formats tool results into natural conversation.",
            user_prompt=prompt
        )
    
    async def _save_to_memory(self, request: ChatRequest, response: Dict[str, Any]):
        """Save conversation to memory."""
        
        # Save user message
        user_message = ChatMessage(
            user_id=request.user_id,
            session_id=request.session_id or "default",
            message_type="user",
            content=request.message,
            timestamp=time.time()
        )
        
        # Save bot response
        bot_message = ChatMessage(
            user_id=request.user_id,
            session_id=request.session_id or "default",
            message_type="bot",
            content=response["text"],
            timestamp=time.time(),
            metadata={
                "processing_mode": response.get("processing_mode"),
                "tools_used": response.get("tools_used", []),
                "sources_count": len(response.get("sources", []))
            }
        )
        
        # Add to memory
        await self.memory_manager.add_message(user_message)
        await self.memory_manager.add_message(bot_message, store_in_long_term=True)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot."""
        return """You are CareerConnect, a professional career assistant chatbot. Your role is to help users with:

1. Job search and career opportunities
2. Career advice and guidance
3. Interview preparation
4. Skill development recommendations
5. Industry insights

Be helpful, professional, and conversational. Provide accurate and actionable advice. If you don't know something, be honest about it and suggest where the user might find more information."""
    
    def _get_tool_selection_prompt(self) -> str:
        """Get the tool selection prompt."""
        return """Based on the user's message, select the most appropriate tool to help them. Consider:
- job_search for finding jobs
- career_advice for career guidance
- interview_preparation for interview help
- skill_development for learning recommendations"""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "available_tools": self.tool_registry.get_tool_names(),
            "memory_stats": self.memory_manager.get_stats(),
            "retriever_available": self.retriever_service is not None
        }


# Global singleton instance
_global_orchestrator: Optional[ChatbotOrchestrator] = None
_orchestrator_lock = asyncio.Lock()


async def get_global_orchestrator() -> ChatbotOrchestrator:
    """Get or create the global orchestrator instance (singleton pattern)."""
    global _global_orchestrator
    
    async with _orchestrator_lock:
        if _global_orchestrator is None:
            logger.info("global_orchestrator_init_start")
            start_time = time.time()
            
            # Initialize services once
            db_session = SessionLocal()
            message_repo = MessageRepository(db_session)
            
            _global_orchestrator = ChatbotOrchestrator(
                llm_service=LLMService(),
                message_repo=message_repo
            )
            
            init_time = time.time() - start_time
            logger.info("global_orchestrator_init_complete", 
                       extra={
                           "init_time": round(init_time, 2)
                       })
        
        return _global_orchestrator


def reset_global_orchestrator():
    """Reset the global orchestrator (for testing/development)."""
    global _global_orchestrator
    _global_orchestrator = None
