"""
Tools registry for managing chatbot tools.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class Tool(ABC):
    """Abstract base class for chatbot tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass


class ToolResult:
    """Result from tool execution."""
    
    def __init__(self, success: bool, result: Any = None, error: str = None):
        self.success = success
        self.result = result
        self.error = error


class ToolRegistry:
    """Registry for managing chatbot tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._auto_discover_tools()
    
    def register_tool(self, tool: Tool):
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_tool_names(self) -> List[str]:
        """Get all registered tool names."""
        return list(self._tools.keys())
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def _auto_discover_tools(self):
        """Auto-discover and register tools from implementations folder."""
        try:
            # This would normally import and register tools
            # For now, we'll create basic mock tools
            pass
        except Exception as e:
            print(f"Failed to auto-discover tools: {e}")


# Mock tools for now


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    
    if _global_registry is None:
        _global_registry = ToolRegistry()
        
        # Register separate tool files
        from app.tools.career_advice_tool import CareerAdviceTool
        from app.tools.job_search_tool import JobSearchTool
        from app.tools.interview_preparation_tool import InterviewPreparationTool
        from app.tools.skill_development_tool import SkillDevelopmentTool
        
        _global_registry.register_tool(CareerAdviceTool())
        _global_registry.register_tool(JobSearchTool())
        _global_registry.register_tool(InterviewPreparationTool())
        _global_registry.register_tool(SkillDevelopmentTool())
    
    return _global_registry


def reset_tool_registry():
    """Reset the global tool registry (for testing)."""
    global _global_registry
    _global_registry = None
