def format_tool_prompt(tool_result: str, user_message: str, context: str = "") -> str:
    return f"""
You are a helpful assistant.

Tool Result:
{tool_result}

User Message:
{user_message}

Conversation Context:
{context}

Task:
Convert the tool result into a natural, helpful, conversational response.
Do not show raw tool output directly.
"""