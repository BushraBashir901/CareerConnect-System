from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .job_application import JobApplicationResponse
from .user import UserResponse


class InterviewBase(BaseModel):
    """
    Base schema for Interview.

    Contains common fields shared across interview-related schemas.
    """
    scheduled_at: datetime
    status: Optional[str] = "pending"


class InterviewCreate(InterviewBase):
    """
    Schema used for creating a new interview.

    Requires references to job application and user.
    """
    job_application_id: int
    user_id: int
    ai_bot_id: Optional[int] = None


class InterviewUpdate(BaseModel):
    """
    Schema used for updating an interview.

    All fields are optional for partial updates.
    """
    scheduled_at: Optional[datetime]
    status: Optional[str]
    ai_bot_id: Optional[int]


class InterviewResponse(InterviewBase):
    """
    Schema used for returning interview data in API responses.

    Includes related job application, user, and AI bot details.
    """
    interview_id: int
    job_application: Optional[JobApplicationResponse] = None
    user: Optional[UserResponse] = None
    ai_bot: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }