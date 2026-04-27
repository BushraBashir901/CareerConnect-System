from typing import Dict, Any, Optional
from app.services.job_search_service import JobSearchService

class JobSearchTool:
    """Chatbot tool for handling job search functionality"""
    
    def __init__(self, job_search_service: JobSearchService):
        self.job_search_service = job_search_service
    
    def search_jobs(self, query: str, user_id: Optional[int] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Search for jobs using semantic similarity.
        
        Args:
            query: Search query describing desired job
            user_id: Optional user ID for personalized search
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results or error message
        """
        try:
            jobs = self.job_search_service.search_jobs_by_text(
                query=query,
                limit=limit,
                user_id=user_id
            )
            
            if not jobs:
                return {
                    "success": False,
                    "message": "I couldn't find any jobs matching your search. Try being more specific about the skills, role, or industry you're interested in.",
                    "jobs": []
                }
            
            return {
                "success": True,
                "message": f"I found {len(jobs)} relevant job opportunities for you:",
                "jobs": jobs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"I encountered an error while searching for jobs: {str(e)}. Please try again.",
                "jobs": []
            }
    
    def get_similar_jobs(self, job_id: int, limit: int = 5) -> Dict[str, Any]:
        """
        Find jobs similar to a specific job.
        
        Args:
            job_id: ID of the reference job
            limit: Maximum number of similar jobs to return
            
        Returns:
            Dictionary with similar job results
        """
        try:
            similar_jobs = self.job_search_service.search_similar_jobs(job_id, limit)
            
            if not similar_jobs:
                return {
                    "success": False,
                    "message": "I couldn't find any similar jobs.",
                    "jobs": []
                }
            
            return {
                "success": True,
                "message": f"Here are {len(similar_jobs)} similar jobs:",
                "jobs": similar_jobs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error finding similar jobs: {str(e)}",
                "jobs": []
            }
    
    def search_jobs_by_location(self, location: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for jobs in a specific location.
        
        Args:
            location: Location to search for
            limit: Maximum number of results
            
        Returns:
            Dictionary with location-based job results
        """
        try:
            jobs = self.job_search_service.get_jobs_by_location(location, limit)
            
            if not jobs:
                return {
                    "success": False,
                    "message": f"I couldn't find any jobs in {location}.",
                    "jobs": []
                }
            
            return {
                "success": True,
                "message": f"I found {len(jobs)} jobs in {location}:",
                "jobs": jobs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching jobs in {location}: {str(e)}",
                "jobs": []
            }
    
    def search_jobs_by_type(self, job_type: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for jobs by type (full-time, part-time, contract, etc.).
        
        Args:
            job_type: Type of employment
            limit: Maximum number of results
            
        Returns:
            Dictionary with job type-based results
        """
        try:
            jobs = self.job_search_service.get_jobs_by_type(job_type, limit)
            
            if not jobs:
                return {
                    "success": False,
                    "message": f"I couldn't find any {job_type} positions.",
                    "jobs": []
                }
            
            return {
                "success": True,
                "message": f"I found {len(jobs)} {job_type} positions:",
                "jobs": jobs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching {job_type} positions: {str(e)}",
                "jobs": []
            }

def format_job_results(result: Dict[str, Any]) -> str:
    """
    Format job search results into a readable string for the chatbot.
    
    Args:
        result: Result dictionary from job search tools
        
    Returns:
        Formatted string for chat response
    """
    if not result["success"]:
        return result["message"]
    
    response = result["message"] + "\n\n"
    
    for i, job in enumerate(result["jobs"], 1):
        response += f"**{i}. {job['job_title']} at {job['company_name']}**\n"
        response += f"{job['location']}\n"
        
        if job.get('job_type'):
            response += f"{job['job_type']}\n"
        
        if job.get('salary_range'):
            response += f"{job['salary_range']}\n"
        
        # Truncate description for readability
        description = job['job_description'][:200] + "..." if len(job['job_description']) > 200 else job['job_description']
        response += f"{description}\n"
        response += f"Match: {job['similarity_score']:.1%}\n\n"
    
    response += "Would you like me to search for more specific roles or help you prepare for applying to any of these positions?"
    
    return response
