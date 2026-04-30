from typing import Optional
from app.services.llm_service import LLMService
from app.services.chatbot_tools.prompts import INTERVIEW_PREPARATION_PROMPT


class InterviewPreparationTool:
    """Chatbot tool for interview preparation"""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    # Interview Tips
    async def get_interview_tips(
        self,
        job_title: str,
        company_type: Optional[str] = None,
        interview_type: Optional[str] = None
    ) -> str:

        prompt = f"Provide comprehensive interview preparation tips for a {job_title} position."

        if company_type:
            prompt += f" The company is a {company_type}."

        if interview_type:
            prompt += f" Focus on {interview_type} interview preparation."

        try:
            return await self.llm.generate(
                system_prompt=INTERVIEW_PREPARATION_PROMPT,
                user_prompt=prompt,
                
            )
        except Exception as e:
            return f"I encountered an error while generating interview tips: {str(e)}"


    # Common Questions
    async def get_common_questions(self, job_title: str) -> str:

        prompt = f"What are the most common interview questions for a {job_title} position? Include both technical and behavioral questions, and provide guidance on how to answer them effectively."

        try:
            return await self.llm.generate(
                system_prompt=INTERVIEW_PREPARATION_PROMPT,
                user_prompt=prompt,
                
            )
        except Exception as e:
            return f"I encountered an error while generating interview questions: {str(e)}"
    
    # Salary Negotiation Tips
    async def get_salary_negotiation_tips(self, job_title: str, experience_level: str) -> str:

        prompt = f"Provide salary negotiation tips and strategies for a {experience_level} {job_title} position. Include research methods, negotiation techniques, and common pitfalls to avoid."

        try:
            return await self.llm.generate(
                system_prompt=INTERVIEW_PREPARATION_PROMPT,
                user_prompt=prompt,
                
            )
        except Exception as e:
            return f"I encountered an error while generating salary negotiation tips: {str(e)}"