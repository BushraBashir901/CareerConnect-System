def messages_key(session_id: str):
    return f"chat:{session_id}:messages"


def summary_key(session_id: str):
    return f"chat:{session_id}:summary"


def count_key(session_id: str):
    return f"chat:{session_id}:count"