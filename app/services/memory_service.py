from datetime import datetime
from app.core.redis_client import redis_client
from app.core.redis_key import messages_key, summary_key, count_key, session_key
from task.message_batch_worker import save_messages_batch

MAX_MESSAGES = 40
RECENT_LIMIT = 10


def add_message(user_id: str, session_id: str, role: str, message: str):
    redis_client.rpush(messages_key(user_id, session_id), f"{role}:{message}")
    redis_client.incr(count_key(user_id, session_id))


def get_recent_messages(user_id: str, session_id: str):
    return redis_client.lrange(messages_key(user_id, session_id), -RECENT_LIMIT, -1)


def get_summary(user_id: str, session_id: str):
    return redis_client.get(summary_key(user_id, session_id))


def set_summary(user_id: str, session_id: str, summary: str):
    redis_client.set(summary_key(user_id, session_id), summary)


def get_message_count(user_id: str, session_id: str) -> int:
    key = f"chat:{user_id}:{session_id}"
    return redis_client.llen(key)


def should_save_to_db(user_id: str, session_id: str):
    return get_message_count(user_id, session_id) >= MAX_MESSAGES


def save_messages_to_db(user_id: str, session_id: str):
    """Save messages to database using background job"""
    messages = redis_client.lrange(messages_key(user_id, session_id), 0, -1)

    formatted_messages = []
    for msg in messages:
        role, content = msg.split(":", 1)
        formatted_messages.append({"role": role, "content": content})

    save_messages_batch.delay(int(user_id), session_id, formatted_messages)


def create_session(user_id: str, session_id: str):
    redis_client.hset(
        session_key(user_id, session_id), "created_at", str(datetime.utcnow())
    )


def close_session(user_id: str, session_id: str):
    save_messages_to_db(user_id, session_id)
    redis_client.hset(
        session_key(user_id, session_id), "closed_at", str(datetime.utcnow())
    )


def reset_memory(user_id: str, session_id: str):
    redis_client.delete(messages_key(user_id, session_id))
    redis_client.delete(count_key(user_id, session_id))


async def update_summary(llm_service, summary, recent_messages):
    prompt = f"""
You are a conversation summarizer.

Old Summary:
{summary or "None"}

New Messages:
{recent_messages}

Create a short updated summary of the conversation.
"""

    return await llm_service.generate(
        system_prompt="You summarize conversations.", user_prompt=prompt
    )
