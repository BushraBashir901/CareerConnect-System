from enum import Enum
from app.core.ai.intent_router import Intent


class Route(str, Enum):
    DIRECT = "direct"
    RAG = "rag"
    TOOL = "tool"
    CLARIFY = "clarify"


class QueryRouter:

    def route(self, intent: Intent, confidence: float):

        # LOW CONFIDENCE → ALWAYS ASK USER
        if confidence < 0.60:
            return Route.CLARIFY

        # -------------------------
        # DIRECT LLM RESPONSES
        # -------------------------
        if intent in [
            Intent.GREETING,
            Intent.SMALL_TALK,
            Intent.GENERAL_QUESTION
        ]:
            return Route.DIRECT

        # -------------------------
        # RAG (VECTOR SEARCH)
        # -------------------------
        if intent in [
            Intent.JOB_SEARCH,
            Intent.RESUME_ANALYSIS
        ]:
            return Route.RAG

        # -------------------------
        # TOOL CALLS (DB / API)
        # -------------------------
        if intent == Intent.TOOL_CALL:
            return Route.TOOL

        # -------------------------
        # FALLBACK
        # -------------------------
        return Route.CLARIFY