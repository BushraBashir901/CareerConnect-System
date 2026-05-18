from celery_worker import celery_app
from app.services.memory_service import (
    get_recent_messages,
    set_summary,
    reset_memory
)
from app.services.llm_service import LLMService
from app.core.logger import logger
import time

llm_service = LLMService()


@celery_app.task(bind=True, max_retries=3)
def summarize_conversation(self, user_id: str, session_id: str):

    start_time = time.time()

    try:
        logger.info("summary_task_started", extra={
            "user_id": user_id,
            "session_id": session_id
        })

        messages = get_recent_messages(user_id, session_id)

        if not messages:
            return {"status": "no_messages"}

        summary = llm_service.generate_sync(
            system_prompt="Summarize this conversation in 2-3 sentences maximum. Keep it very concise.",
            user_prompt=str(messages)
        )

        # ✅ correct key usage
        set_summary(user_id, session_id, summary)

        reset_memory(user_id, session_id)

        logger.info("summary_task_completed", extra={
            "user_id": user_id,
            "session_id": session_id,
            "processing_time": time.time() - start_time
        })

        return {"status": "done"}

    except Exception as e:
        logger.error("summary_task_failed", extra={"error": str(e)})
        raise self.retry(exc=e, countdown=5)