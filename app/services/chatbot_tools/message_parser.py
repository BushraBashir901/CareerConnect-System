from typing import Dict, Any, Tuple
import re

class MessageParser:
    """Utility class to parse and categorize user messages"""
    
    def __init__(self):
        self.job_search_keywords = [
            "find jobs", "search jobs", "job search", "looking for job",
            "job opportunities", "find me a job", "search for", "job openings",
            "vacancies", "positions", "roles", "hiring", "employment",
            "career opportunities", "work", "apply"
        ]
        
        self.career_advice_keywords = [
            "career advice", "career guidance", "advice", "guidance",
            "career path", "career development", "professional development",
            "career growth", "future career", "career change"
        ]
        
        self.interview_keywords = [
            "interview", "interview preparation", "interview tips",
            "prepare for interview", "interview questions", "technical interview",
            "behavioral interview", "mock interview", "salary negotiation"
        ]
        
        self.skill_keywords = [
            "skills", "learn skills", "develop skills", "skill development",
            "technical skills", "soft skills", "new skills", "improve skills"
        ]
        
        self.location_patterns = [
            r"in\s+(\w+(?:\s+\w+)*)",  # "in New York"
            r"at\s+(\w+(?:\s+\w+)*)",   # "at Google"
            r"near\s+(\w+(?:\s+\w+)*)",  # "near Boston"
            r"(\w+)\s+area",            # "Bay area"
        ]
        
        self.job_type_patterns = [
            r"(full[-\s]?time|full[-\s]?time)",
            r"(part[-\s]?time|part[-\s]?time)",
            r"(contract|contractor)",
            r"(remote|work from home|wfh)",
            r"(hybrid|flexible)",
            r"(internship|intern)",
            r"(freelance|freelancer)"
        ]
    
    def categorize_message(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Categorize user message and extract relevant information.
        
        Args:
            message: User message text
            
        Returns:
            Tuple of (category, extracted_info)
        """
        message_lower = message.lower()
        
        # Check for job search intent
        if any(keyword in message_lower for keyword in self.job_search_keywords):
            category = "job_search"
            info = self._extract_job_search_info(message)
            return category, info
        
        # Check for interview preparation
        elif any(keyword in message_lower for keyword in self.interview_keywords):
            category = "interview"
            info = self._extract_interview_info(message)
            return category, info
        
        # Check for career advice
        elif any(keyword in message_lower for keyword in self.career_advice_keywords):
            category = "career_advice"
            info = self._extract_career_advice_info(message)
            return category, info
        
        # Check for skill development
        elif any(keyword in message_lower for keyword in self.skill_keywords):
            category = "skill_development"
            info = self._extract_skill_info(message)
            return category, info
        
        # Default to general conversation
        else:
            category = "general"
            info = self._extract_general_info(message)
            return category, info
    
    def _extract_job_search_info(self, message: str) -> Dict[str, Any]:
        """Extract job search parameters from message"""
        info = {
            "query": message,
            "location": None,
            "job_type": None,
            "keywords": []
        }
        
        # Extract location
        for pattern in self.location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info["location"] = match.group(1).strip()
                break
        
        # Extract job type
        for pattern in self.job_type_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info["job_type"] = match.group(1).replace("-", " ").strip()
                break
        
        # Extract technical keywords (simplified)
        tech_keywords = [
            "python", "java", "javascript", "react", "node", "sql", "aws",
            "docker", "kubernetes", "machine learning", "data science",
            "frontend", "backend", "full stack", "devops", "mobile",
            "android", "ios", "web development", "software engineer"
        ]
        
        message_lower = message.lower()
        info["keywords"] = [kw for kw in tech_keywords if kw in message_lower]
        
        return info
    
    def _extract_interview_info(self, message: str) -> Dict[str, Any]:
        """Extract interview information from message"""
        info = {
            "job_title": None,
            "company_type": None,
            "interview_type": None,
            "experience_level": None
        }
        
        # Extract job title (simplified pattern matching)
        job_titles = [
            "software engineer", "developer", "data scientist", "product manager",
            "designer", "analyst", "consultant", "manager", "engineer"
        ]
        
        message_lower = message.lower()
        for title in job_titles:
            if title in message_lower:
                info["job_title"] = title
                break
        
        # Extract company type
        if "startup" in message_lower:
            info["company_type"] = "startup"
        elif "enterprise" in message_lower or "large company" in message_lower:
            info["company_type"] = "enterprise"
        
        # Extract interview type
        if "technical" in message_lower:
            info["interview_type"] = "technical"
        elif "behavioral" in message_lower:
            info["interview_type"] = "behavioral"
        
        # Extract experience level
        levels = ["entry level", "junior", "mid level", "senior", "lead", "principal"]
        for level in levels:
            if level in message_lower:
                info["experience_level"] = level
                break
        
        return info
    
    def _extract_career_advice_info(self, message: str) -> Dict[str, Any]:
        """Extract career advice information from message"""
        info = {
            "field": None,
            "experience_level": None,
            "specific_context": message
        }
        
        # Extract field/industry
        fields = [
            "technology", "software", "data science", "finance", "healthcare",
            "marketing", "sales", "education", "consulting", "engineering"
        ]
        
        message_lower = message.lower()
        for field in fields:
            if field in message_lower:
                info["field"] = field
                break
        
        # Extract experience level
        levels = ["entry level", "junior", "mid level", "senior", "lead", "principal"]
        for level in levels:
            if level in message_lower:
                info["experience_level"] = level
                break
        
        return info
    
    def _extract_skill_info(self, message: str) -> Dict[str, Any]:
        """Extract skill development information from message"""
        info = {
            "current_role": None,
            "target_role": None,
            "skill_type": None
        }
        
        message_lower = message.lower()
        
        # Extract current and target roles
        if "transition" in message_lower or "move to" in message_lower:
            # Look for role transitions
            roles = ["developer", "manager", "engineer", "analyst", "designer"]
            for role in roles:
                if role in message_lower:
                    if not info["current_role"]:
                        info["current_role"] = role
                    else:
                        info["target_role"] = role
                        break
        
        # Extract skill type
        if "technical" in message_lower:
            info["skill_type"] = "technical"
        elif "soft" in message_lower:
            info["skill_type"] = "soft"
        
        return info
    
    def _extract_general_info(self, message: str) -> Dict[str, Any]:
        """Extract general information from message"""
        return {
            "message": message,
            "intent": "general_conversation"
        }
