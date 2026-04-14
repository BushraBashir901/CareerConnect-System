from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserResponse
from .job import JobResponse


class JobApplicationBase(BaseModel):
    """
    Base schema for Job Application.

    Contains common fields shared across job application schemas.
    """
    applied_at: Optional[datetime] = None


class JobApplicationCreate(BaseModel):
    """
    Schema used for creating a new job application.

    Requires user and job references.
    """
    job_id: int
    user_id: int


class JobApplicationUpdate(BaseModel):
    """
    Schema used for updating a job application.

    Currently not used, kept for future extension.
    """
    pass


class JobApplicationResponse(JobApplicationBase):
    """
    Schema used for returning job application data in API responses.

    Includes related user and job details.
    """
    job_id: int
    user_id: int
    job: Optional[JobResponse] = None
    user: Optional[UserResponse] = None

    model_config = {
        "from_attributes": True
    }