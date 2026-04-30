from app.core.llm_client import client


class LLMService:
    """
    Central LLM service for all AI calls.
    """

    def __init__(self):
        self.client = client

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7):
        """
        Single entry point for all LLM calls.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"LLM Error: {str(e)}"