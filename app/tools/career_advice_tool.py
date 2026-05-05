"""Career advice tool implementation."""

from typing import Dict, Any
from app.tools.registry import Tool, ToolResult
from app.prompts.career_advice import CAREER_ADVICE_SYSTEM_PROMPT, CAREER_ADVICE_USER_PROMPT


class CareerAdviceTool(Tool):
    """Tool for providing career advice and guidance."""
    
    def __init__(self):
        super().__init__(
            "career_advice", 
            "Provides professional career advice and guidance"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute career advice tool."""
        query = parameters.get("query", "general career advice")
        
        # Format the prompt with user query
        user_prompt = CAREER_ADVICE_USER_PROMPT.format(query=query)
        
        # In a real implementation, this would call LLM service
        # For now, return a mock response
        advice = f"""Career advice for '{query}':

1. **Assess Your Current Position**: Evaluate your skills, experience, and what you enjoy doing.

2. **Research Growth Areas**: Look into industries projected to grow in the next 5-10 years.

3. **Skill Development**: Identify gaps in your skillset and create a learning plan.

4. **Networking**: Build professional relationships in your target industry.

5. **Set SMART Goals**: Create specific, measurable, achievable, relevant, and time-bound career objectives.

Would you like more specific advice on any of these areas?"""
        
        return ToolResult(success=True, result=advice)
