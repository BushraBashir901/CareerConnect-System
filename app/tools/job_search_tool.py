"""Job search tool implementation."""

from typing import Dict, Any
from app.tools.registry import Tool, ToolResult
from app.prompts.job_search import JOB_SEARCH_SYSTEM_PROMPT, JOB_SEARCH_USER_PROMPT


class JobSearchTool(Tool):
    """Tool for searching job opportunities."""
    
    def __init__(self):
        super().__init__(
            "job_search", 
            "Searches for job opportunities and provides listings"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute job search tool."""
        query = parameters.get("query", "software engineer")
        location = parameters.get("location", "remote")
        
        # Format the prompt with user parameters
        user_prompt = JOB_SEARCH_USER_PROMPT.format(query=query, location=location)
        
        # In a real implementation, this would call LLM service
        # For now, return mock job listings
        jobs = f"""Found 5 {query} jobs in {location}:

1. **Senior {query.title()}** at TechCorp
   - Requirements: 5+ years experience, Python/JavaScript
   - Salary: $120k-$150k
   - Remote: Yes

2. **{query.title()}** at StartupXYZ
   - Requirements: 3+ years experience, React/Node.js
   - Salary: $90k-$120k
   - Remote: Hybrid

3. **Lead {query}** at EnterpriseCo
   - Requirements: 7+ years experience, cloud architecture
   - Salary: $150k-$180k
   - Remote: Yes

4. **{query.title()}** at DigitalAgency
   - Requirements: 2+ years experience, web development
   - Salary: $70k-$90k
   - Location: {location.title()}

5. **{query.title()}** at GovTech
   - Requirements: Security clearance, government experience
   - Salary: $100k-$130k
   - Remote: Yes

Apply through company career pages or job boards!"""
        
        return ToolResult(success=True, result=jobs)
