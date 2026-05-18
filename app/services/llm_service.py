from typing import List, Dict, Optional
from app.core.llm_client import client
from app.core.config import settings


class LLMService:

    def __init__(self):
        self.client = client
        self.model = settings.OPENAI_API_KEY

    # -----------------------------
    # CORE CALL (NO DUPLICATION)
    # -----------------------------
    def _create_completion(self, messages: List[Dict]):

        return self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

    # -----------------------------
    # MESSAGE BUILDER
    # -----------------------------
    def _build_messages(
        self,
        system_prompt: str,
        messages: Optional[List[Dict]] = None,
        user_prompt: Optional[str] = None
    ):

        final_messages = [
            {"role": "system", "content": system_prompt}
        ]

        if messages:
            final_messages.extend(self._sanitize_messages(messages))

        if user_prompt:
            final_messages.append(
                {"role": "user", "content": user_prompt}
            )

        return final_messages

    # -----------------------------
    # ASYNC (FASTAPI)
    # -----------------------------
    async def generate(
        self,
        system_prompt: str,
        messages: Optional[List[Dict]] = None,
        user_prompt: Optional[str] = None
    ) -> str:

        final_messages = self._build_messages(
            system_prompt,
            messages,
            user_prompt
        )

        response = self._create_completion(final_messages)

        return response.choices[0].message.content

    # -----------------------------
    # SYNC (CELERY)
    # -----------------------------
    def generate_sync(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:

        final_messages = self._build_messages(
            system_prompt,
            user_prompt=user_prompt
        )

        response = self._create_completion(final_messages)

        return response.choices[0].message.content

    # -----------------------------
    # SANITIZER
    # -----------------------------
    def _sanitize_messages(self, messages: List[Dict]) -> List[Dict]:

        clean_messages = []

        for m in messages:
            if not isinstance(m, dict):
                continue
            if "role" not in m or "content" not in m:
                continue

            clean_messages.append({
                "role": m["role"],
                "content": str(m["content"])
            })

        return clean_messages