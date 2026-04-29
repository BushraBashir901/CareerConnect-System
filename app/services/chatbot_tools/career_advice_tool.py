from typing import Optional
from app.core.llm_client import client
from app.services.chatbot_tools.prompts import CAREER_ADVICE_PROMPT, INTERVIEW_PREPARATION_PROMPT

class CareerAdviceTool:
    """Chatbot tool for providing career guidance and advice"""
    
    def __init__(self):
        self.client = client
    
    async def get_career_advice(self, field: str, experience_level: str, specific_context: Optional[str] = None) -> str:
        """
        Get career advice for a specific field and experience level.
        
        Args:
            field: Career field or industry
            experience_level: Experience level (entry-level, mid-level, senior, etc.)
            specific_context: Additional context about the person's situation
            
        Returns:
            Personalized career advice
        """
        prompt = f"Provide comprehensive career advice for someone in the {field} field with {experience_level} experience level."
        
        if specific_context:
            prompt += f" Additional context: {specific_context}"
        
        try:
            messages = [
                {"role": "system", "content": CAREER_ADVICE_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating career advice: {str(e)}"
    
    async def get_skill_recommendations(self, current_role: str, target_role: Optional[str] = None) -> str:
        """
        Get skill development recommendations.
        
        Args:
            current_role: Current job role
            target_role: Desired future role (optional)
            
        Returns:
            Skill development recommendations
        """
        if target_role:
            prompt = f"What skills should someone develop to transition from {current_role} to {target_role}? Include both technical and soft skills."
        else:
            prompt = f"What skills should someone in {current_role} focus on developing for career growth?"
        
        try:
            messages = [
                {"role": "system", "content": CAREER_ADVICE_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating skill recommendations: {str(e)}"
    
    async def get_industry_insights(self, industry: str) -> str:
        """
        Get insights about a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Industry insights and trends
        """
        prompt = f"Provide current insights, trends, and future outlook for the {industry} industry. Include job market conditions, emerging opportunities, and key challenges."
        
        try:
            messages = [
                {"role": "system", "content": CAREER_ADVICE_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating industry insights: {str(e)}"

class InterviewPreparationTool:
    """Chatbot tool for interview preparation"""
    
    def __init__(self):
        self.client = client
    
    async def get_interview_tips(self, job_title: str, company_type: Optional[str] = None, interview_type: Optional[str] = None) -> str:
        """
        Get interview preparation tips for a specific job.
        
        Args:
            job_title: Position being interviewed for
            company_type: Type of company (startup, enterprise, etc.)
            interview_type: Type of interview (technical, behavioral, etc.)
            
        Returns:
            Interview preparation advice
        """
        prompt = f"Provide comprehensive interview preparation tips for a {job_title} position."
        
        if company_type:
            prompt += f" The company is a {company_type}."
        
        if interview_type:
            prompt += f" Focus on {interview_type} interview preparation."
        
        try:
            messages = [
                {"role": "system", "content": INTERVIEW_PREPARATION_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating interview tips: {str(e)}"
    
    async def get_common_questions(self, job_title: str) -> str:
        """
        Get common interview questions for a specific role.
        
        Args:
            job_title: Job title
            
        Returns:
            List of common interview questions and how to approach them
        """
        prompt = f"What are the most common interview questions for a {job_title} position? Include both technical and behavioral questions, and provide guidance on how to answer them effectively."
        
        try:
            messages = [
                {"role": "system", "content": INTERVIEW_PREPARATION_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating interview questions: {str(e)}"
    
    async def get_salary_negotiation_tips(self, job_title: str, experience_level: str) -> str:
        """
        Get salary negotiation advice.
        
        Args:
            job_title: Job title
            experience_level: Experience level
            
        Returns:
            Salary negotiation tips and strategies
        """
        prompt = f"Provide salary negotiation tips and strategies for a {experience_level} {job_title} position. Include research methods, negotiation techniques, and common pitfalls to avoid."
        
        try:
            messages = [
                {"role": "system", "content": INTERVIEW_PREPARATION_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I encountered an error while generating salary negotiation tips: {str(e)}"
