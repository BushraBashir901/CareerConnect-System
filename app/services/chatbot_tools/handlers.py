"""
Chatbot message handlers for different types of user requests.
Separates the handling logic from the main service for better organization.
"""

from typing import Dict, Any, Optional
from app.services.chatbot_tools.job_search_tool import JobSearchTool, format_job_results
from app.services.chatbot_tools.career_advice_tool import CareerAdviceTool, InterviewPreparationTool

class ChatbotHandlers:
    """Collection of message handlers for different chatbot functionalities"""
    
    def __init__(self, 
                 job_search_tool: Optional[JobSearchTool] = None,
                 career_advice_tool: Optional[CareerAdviceTool] = None,
                 interview_tool: Optional[InterviewPreparationTool] = None):
        self.job_search_tool = job_search_tool
        self.career_advice_tool = career_advice_tool
        self.interview_tool = interview_tool
    
    async def handle_job_search(self, info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Handle job search requests using the job search tool"""
        if not self.job_search_tool:
            return "Job search service is not available. Please contact support."
        
        user_id = context.get("user_id") if context else None
        query = info.get("query", "")
        
        # Perform job search
        result = self.job_search_tool.search_jobs(query, user_id)
        
        # Format and return results
        return format_job_results(result)
    
    async def handle_interview(self, info: Dict[str, Any]) -> str:
        """Handle interview preparation requests"""
        if not self.interview_tool:
            return "Interview preparation service is not available. Please contact support."
        
        job_title = info.get("job_title") or "your position"
        company_type = info.get("company_type")
        interview_type = info.get("interview_type")
        
        return await self.interview_tool.get_interview_tips(job_title, company_type, interview_type)
    
    async def handle_career_advice(self, info: Dict[str, Any]) -> str:
        """Handle career advice requests"""
        if not self.career_advice_tool:
            return "Career advice service is not available. Please contact support."
        
        field = info.get("field") or "your field"
        experience_level = info.get("experience_level") or "your experience level"
        specific_context = info.get("specific_context")
        
        return await self.career_advice_tool.get_career_advice(field, experience_level, specific_context)
    
    async def handle_skill_development(self, info: Dict[str, Any]) -> str:
        """Handle skill development requests"""
        if not self.career_advice_tool:
            return "Skill development service is not available. Please contact support."
        
        current_role = info.get("current_role") or "your current role"
        target_role = info.get("target_role")
        
        return await self.career_advice_tool.get_skill_recommendations(current_role, target_role)
    
    async def handle_location_search(self, info: Dict[str, Any]) -> str:
        """Handle location-based job search"""
        if not self.job_search_tool:
            return "Job search service is not available. Please contact support."
        
        location = info.get("location")
        if not location:
            return "Please specify a location for the job search."
        
        result = self.job_search_tool.search_jobs_by_location(location)
        return format_job_results(result)
    
    async def handle_job_type_search(self, info: Dict[str, Any]) -> str:
        """Handle job type-based job search"""
        if not self.job_search_tool:
            return "Job search service is not available. Please contact support."
        
        job_type = info.get("job_type")
        if not job_type:
            return "Please specify a job type (full-time, part-time, contract, remote, etc.)."
        
        result = self.job_search_tool.search_jobs_by_type(job_type)
        return format_job_results(result)
    
    async def handle_similar_jobs(self, job_id: int) -> str:
        """Handle similar job recommendations"""
        if not self.job_search_tool:
            return "Job search service is not available. Please contact support."
        
        result = self.job_search_tool.get_similar_jobs(job_id)
        return format_job_results(result)
    
    async def handle_common_questions(self, info: Dict[str, Any]) -> str:
        """Handle requests for common interview questions"""
        if not self.interview_tool:
            return "Interview preparation service is not available. Please contact support."
        
        job_title = info.get("job_title") or "your position"
        return await self.interview_tool.get_common_questions(job_title)
    
    async def handle_salary_negotiation(self, info: Dict[str, Any]) -> str:
        """Handle salary negotiation advice requests"""
        if not self.interview_tool:
            return "Interview preparation service is not available. Please contact support."
        
        job_title = info.get("job_title") or "your position"
        experience_level = info.get("experience_level") or "your experience level"
        
        return await self.interview_tool.get_salary_negotiation_tips(job_title, experience_level)
    
    async def handle_industry_insights(self, info: Dict[str, Any]) -> str:
        """Handle industry insights requests"""
        if not self.career_advice_tool:
            return "Career advice service is not available. Please contact support."
        
        industry = info.get("industry") or "your industry"
        return await self.career_advice_tool.get_industry_insights(industry)
    
    # Legacy methods for backward compatibility
    async def get_career_advice(self, field: str, experience_level: str) -> str:
        """Get specific career advice based on field and experience"""
        return await self.handle_career_advice({
            "field": field,
            "experience_level": experience_level
        })
    
    async def interview_preparation(self, job_title: str, company_type: str = None) -> str:
        """Get interview preparation tips for a specific job"""
        return await self.handle_interview({
            "job_title": job_title,
            "company_type": company_type
        })
    
    async def search_jobs(self, query: str, user_id: Optional[int] = None) -> str:
        """Direct job search method"""
        if not self.job_search_tool:
            return "Job search service is not available. Please contact support."
        
        result = self.job_search_tool.search_jobs(query, user_id)
        return format_job_results(result)
