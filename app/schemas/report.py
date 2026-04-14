from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import UserResponse
from .ai_bot import AiBotResponse
from .company import CompanyResponse


class ReportBase(BaseModel):
    """
    Base schema for Report.

    Contains common fields shared across report creation, update, and response schemas.
    """
    score: int
    result: str
    remarks: Optional[str] = None


class ReportCreate(ReportBase):
    """
    Schema used for creating a new report.

    Includes foreign key references required to create a report record.
    """
    user_id: int
    bot_id: int
    company_id: int


class ReportUpdate(BaseModel):
    """
    Schema used for updating an existing report.

    All fields are optional to allow partial updates.
    """
    score: Optional[int]
    result: Optional[str]
    remarks: Optional[str]


class ReportResponse(ReportBase):
    """
    Schema used for returning report data in API responses.

    Includes related nested entities like user, bot, and company.
    """
    report_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None
    bot: Optional[AiBotResponse] = None
    company: Optional[CompanyResponse] = None

    model_config = {
        "from_attributes": True
    }