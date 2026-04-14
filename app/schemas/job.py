from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .company import CompanyResponse


class JobBase(BaseModel):
    """
    Base schema for Job.

    Contains common job-related fields shared across create, update, and response schemas.
    """
    job_title: str
    job_description: str
    location: str
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = True


class JobCreate(JobBase):
    """
    Schema used for creating a new job.
    Inherits all fields from JobBase.
    """
    pass


class JobUpdate(BaseModel):
    """
    Schema used for updating an existing job.

    All fields are optional to allow partial updates.
    """
    job_title: Optional[str]=None   
    job_description: Optional[str]=None
    location: Optional[str]=None
    salary_range: Optional[str]=None
    job_type: Optional[str]=None
    is_active: Optional[bool]=None
    company_id: Optional[int]=None


class JobResponse(JobBase):
    """
    Schema used for returning job data in API responses.

    Includes related company information and database-generated fields.
    """
    job_id: int
    created_at: datetime
    company_id: int 

    model_config = {
        "from_attributes": True
    }