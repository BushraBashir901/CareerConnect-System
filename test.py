from app.services.memory_service import add_message, get_recent_messages
from app.core.redis_client import redis_client

session_id = "test123"

add_message(session_id, "user", "hello")
add_message(session_id, "assistant", "hi!")

print(get_recent_messages(session_id))