from celery_worker import celery_app
from app.services.memory_service import (
    get_recent_messages,
    set_summary,
    reset_memory
)

from app.services.llm_service import LLMService

llm_service = LLMService()


@celery_app.task
def summarize_conversation(session_id: str):

    messages = get_recent_messages(session_id)

    if not messages:
        return

    summary = llm_service.generate_sync(
        system_prompt="Summarize this conversation in short form.",
        user_prompt=str(messages)
    )

    set_summary(session_id, summary)
    reset_memory(session_id)

    return {"status": "done", "session_id": session_id}