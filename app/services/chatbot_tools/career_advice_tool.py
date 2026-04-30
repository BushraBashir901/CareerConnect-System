from typing import Optional
from app.services.llm_service import LLMService
from app.services.chatbot_tools.prompts import CAREER_ADVICE_PROMPT


class CareerAdviceTool:
    """Chatbot tool for providing career guidance and advice"""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    # Career Advice
    async def get_career_advice(
        self,
        field: str,
        experience_level: str,
        specific_context: Optional[str] = None
    ) -> str:

        prompt = f"Provide comprehensive career advice for someone in the {field} field with {experience_level} experience level."

        if specific_context:
            prompt += f" Additional context: {specific_context}"

        try:
            return await self.llm.generate(
                system_prompt=CAREER_ADVICE_PROMPT,
                user_prompt=prompt,
                
            )

        except Exception as e:
            return f"I encountered an error while generating career advice: {str(e)}"

    # Skill Recommendations
    async def get_skill_recommendations(
        self,
        current_role: str,
        target_role: Optional[str] = None
    ) -> str:

        if target_role:
            prompt = f"What skills should someone develop to transition from {current_role} to {target_role}? Include both technical and soft skills."
        else:
            prompt = f"What skills should someone in {current_role} focus on developing for career growth?"

        try:
            return await self.llm.generate(
                system_prompt=CAREER_ADVICE_PROMPT,
                user_prompt=prompt,
                
            )

        except Exception as e:
            return f"I encountered an error while generating skill recommendations: {str(e)}"

    # Industry Insights
    async def get_industry_insights(self, industry: str) -> str:

        prompt = f"Provide current insights, trends, and future outlook for the {industry} industry. Include job market conditions, emerging opportunities, and key challenges."

        try:
            return await self.llm.generate(
                system_prompt=CAREER_ADVICE_PROMPT,
                user_prompt=prompt,
                
            )

        except Exception as e:
            return f"I encountered an error while generating industry insights: {str(e)}"