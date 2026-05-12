def messages_key(user_id: str, session_id: str):
    return f"user:{user_id}:session:{session_id}:messages"


def summary_key(user_id: str, session_id: str):
    return f"user:{user_id}:session:{session_id}:summary"


def count_key(user_id: str, session_id: str):
    return f"user:{user_id}:session:{session_id}:count"


def session_key(user_id: str, session_id: str):
    return f"user:{user_id}:session:{session_id}:info"