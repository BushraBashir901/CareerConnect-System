from app.core.redis_client import redis_client
from app.core.redis_key import messages_key, summary_key, count_key


# -----------------------------
# ADD MESSAGE (REAL MEMORY)
# -----------------------------
def add_message(user_id: str, session_id: str, role: str, message: str):
    redis_client.rpush(
        messages_key(user_id, session_id),
        f"{role}:{message}"
    )

    redis_client.incr(count_key(user_id, session_id))


# -----------------------------
# GET RECENT MESSAGES
# -----------------------------
def get_recent_messages(user_id: str, session_id: str):
    return redis_client.lrange(
        messages_key(user_id, session_id),
        -10,
        -1
    )


# -----------------------------
# SUMMARY
# -----------------------------
def get_summary(user_id: str, session_id: str):
    return redis_client.get(summary_key(user_id, session_id))


def set_summary(user_id: str, session_id: str, summary: str):
    redis_client.set(summary_key(user_id, session_id), summary)


# -----------------------------
# COUNT (FIXED)
# -----------------------------
def get_message_count(user_id: str, session_id: str) -> int:
    return redis_client.llen(messages_key(user_id, session_id))


# -----------------------------
# RESET MEMORY
# -----------------------------
def reset_memory(user_id: str, session_id: str):
    redis_client.delete(messages_key(user_id, session_id))
    redis_client.delete(count_key(user_id, session_id))