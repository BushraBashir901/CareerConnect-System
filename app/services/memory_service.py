from app.core.redis_client import redis_client
from app.core.redis_key import messages_key, summary_key, count_key

MAX_MESSAGES = 40
RECENT_LIMIT = 10

def add_message(session_id: str, role: str, message: str):
    redis_client.rpush(
        messages_key(session_id),
        f"{role}:{message}"
    )

    redis_client.incr(count_key(session_id))


def get_recent_messages(session_id: str):
    return redis_client.lrange(
        messages_key(session_id),
        -RECENT_LIMIT,
        -1
    )

def get_summary(session_id: str):
    return redis_client.get(summary_key(session_id))


def set_summary(session_id: str, summary: str):
    redis_client.set(summary_key(session_id), summary)


def should_summarize(session_id: str):
    count = redis_client.get(count_key(session_id))
    return count and int(count) >= MAX_MESSAGES

def reset_memory(session_id: str):
    redis_client.delete(messages_key(session_id))
    redis_client.delete(count_key(session_id))