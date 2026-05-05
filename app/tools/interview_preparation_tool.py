"""Interview preparation tool implementation."""

from typing import Dict, Any
from app.tools.registry import Tool, ToolResult
from app.prompts.interview_preparation import INTERVIEW_PREP_SYSTEM_PROMPT, INTERVIEW_PREP_USER_PROMPT


class InterviewPreparationTool(Tool):
    """Tool for helping users prepare for job interviews."""
    
    def __init__(self):
        super().__init__(
            "interview_preparation", 
            "Helps prepare for job interviews with tips and practice questions"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute interview preparation tool."""
        role = parameters.get("role", "software engineer")
        
        # Format prompt with user role
        user_prompt = INTERVIEW_PREP_USER_PROMPT.format(role=role)
        
        # In a real implementation, this would call LLM service
        # For now, return mock interview preparation
        prep = f"""Interview preparation for {role.title()}:

**Common Interview Questions:**
1. "Tell me about your experience with {role.lower()} responsibilities."
2. "How do you handle tight deadlines and pressure?"
3. "Describe a challenging project you've worked on."
4. "Where do you see yourself in 5 years?"
5. "Why do you want to work for our company?"

**Best Practices:**
- Research the company beforehand
- Prepare STAR method examples (Situation, Task, Action, Result)
- Dress professionally for video/in-person interviews
- Bring thoughtful questions about the role and team

**Questions to Ask:**
- "What does success look like in this role?"
- "How does the team collaborate on projects?"
- "What are the biggest challenges the team is facing?"
- "What opportunities for professional development are available?"

**Tips for Success:**
- Arrive 10-15 minutes early
- Maintain eye contact and good posture
- Listen carefully before responding
- Follow up with a thank you email

Good luck with your interview!"""
        
        return ToolResult(success=True, result=prep)
