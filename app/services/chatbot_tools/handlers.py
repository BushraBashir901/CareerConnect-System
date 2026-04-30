from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.chatbot_tools.job_search_tool import JobSearchTool
    from app.services.chatbot_tools.career_advice_tool import CareerAdviceTool
    from app.services.chatbot_tools.interviewpreparation_tool import InterviewPreparationTool
from app.services.chatbot_tools.job_search_tool import format_job_results


class ChatbotHandlers:
    """Collection of message handlers for chatbot routing"""

    def __init__(
        self,
        job_search_tool: Optional['JobSearchTool'] = None,
        career_advice_tool: Optional['CareerAdviceTool'] = None,
        interview_tool: Optional['InterviewPreparationTool'] = None
    ):
        self.job_search_tool = job_search_tool
        self.career_advice_tool = career_advice_tool
        self.interview_tool = interview_tool

    
    # JOB SEARCH HANDLERS
    async def handle_job_search(self, info: Dict[str, Any], context: Dict[str, Any] = None) -> str:

        if not self.job_search_tool:
            return "Job search service is not available."

        user_id = context.get("user_id") if context else None
        query = info.get("query", "")

        result = await self.job_search_tool.search_jobs(query, user_id)

        return format_job_results(result)

    async def handle_location_search(self, info: Dict[str, Any]) -> str:

        if not self.job_search_tool:
            return "Job search service is not available."

        location = info.get("location")
        if not location:
            return "Please specify a location."

        result = await self.job_search_tool.search_jobs_by_location(location)

        return format_job_results(result)

    async def handle_job_type_search(self, info: Dict[str, Any]) -> str:

        if not self.job_search_tool:
            return "Job search service is not available."

        job_type = info.get("job_type")
        if not job_type:
            return "Please specify job type."

        result = await self.job_search_tool.search_jobs_by_type(job_type)

        return format_job_results(result)

    async def handle_similar_jobs(self, job_id: int) -> str:

        if not self.job_search_tool:
            return "Job search service is not available."

        result = await self.job_search_tool.get_similar_jobs(job_id)

        return format_job_results(result)

    # CAREER ADVICE
    async def handle_career_advice(self, info: Dict[str, Any]) -> str:

        if not self.career_advice_tool:
            return "Career advice service is not available."

        return await self.career_advice_tool.get_career_advice(
            info.get("field", "your field"),
            info.get("experience_level", "your level"),
            info.get("specific_context")
        )

    async def handle_skill_development(self, info: Dict[str, Any]) -> str:

        if not self.career_advice_tool:
            return "Career service is not available."

        return await self.career_advice_tool.get_skill_recommendations(
            info.get("current_role", "your role"),
            info.get("target_role")
        )

    async def handle_industry_insights(self, info: Dict[str, Any]) -> str:

        if not self.career_advice_tool:
            return "Career service is not available."

        return await self.career_advice_tool.get_industry_insights(
            info.get("industry", "your industry")
        )

  
    # INTERVIEW
    async def handle_interview(self, info: Dict[str, Any]) -> str:

        if not self.interview_tool:
            return "Interview service is not available."

        return await self.interview_tool.get_interview_tips(
            info.get("job_title", "your position"),
            info.get("company_type"),
            info.get("interview_type")
        )

    async def handle_common_questions(self, info: Dict[str, Any]) -> str:

        if not self.interview_tool:
            return "Interview service is not available."

        return await self.interview_tool.get_common_questions(
            info.get("job_title", "your position")
        )

    async def handle_salary_negotiation(self, info: Dict[str, Any]) -> str:

        if not self.interview_tool:
            return "Interview service is not available."

        return await self.interview_tool.get_salary_negotiation_tips(
            info.get("job_title", "your position"),
            info.get("experience_level", "your level")
        )

    # LEGACY WRAPPERS
    async def search_jobs(self, query: str, user_id: Optional[int] = None) -> str:
        return await self.handle_job_search({"query": query}, {"user_id": user_id})