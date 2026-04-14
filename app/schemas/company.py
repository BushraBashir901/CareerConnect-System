from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List


class CompanyBase(BaseModel):
    """
    Base schema for Company.

    Contains common fields shared across create, update, and response schemas.
    """
    company_name: str
    description: Optional[str] = None
    website: Optional[HttpUrl] = None


class CompanyCreate(CompanyBase):
    """
    Schema used for creating a new company.

    Inherits all fields from CompanyBase.
    """
    pass


class CompanyUpdate(BaseModel):
    """
    Schema used for updating an existing company.

    All fields are optional to allow partial updates.
    """
    company_name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None


class CompanyResponse(CompanyBase):
    """
    Schema used for returning company data in API responses.

    Includes database-generated fields.
    """
    company_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }