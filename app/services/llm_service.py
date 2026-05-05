from typing import List, Dict, Optional
from app.core.llm_client import client


class LLMService:

    def __init__(self):
        self.client = client

    async def generate(
        self,
        system_prompt: str,
        messages: Optional[List[Dict]] = None,
        user_prompt: Optional[str] = None
    ) -> str:

        try:
           
            final_messages = []

            # system prompt always first
            final_messages.append({
                "role": "system",
                "content": system_prompt
            })

            # history/messages
            if messages:
                final_messages.extend(self._sanitize_messages(messages))

            # fallback user prompt (if not using full messages flow)
            if user_prompt:
                final_messages.append({
                    "role": "user",
                    "content": user_prompt
                })

        
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=final_messages
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"LLM Error: {str(e)}"

 
    def _sanitize_messages(self, messages: List[Dict]) -> List[Dict]:
        clean = []

        for msg in messages:
            if not isinstance(msg, dict):
                continue

            if "role" not in msg or "content" not in msg:
                continue

            clean.append({
                "role": msg["role"],
                "content": str(msg["content"])
            })

        return clean