from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from .company import CompanyResponse


class UserBase(BaseModel):
    """
    Base schema for User with strict RBAC requirements.

    Contains common user fields shared across create, update, and response schemas.
    """
    username: str
    email: EmailStr
    role: str  # Required field for RBAC
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """
    Schema used for creating a new user.

    Includes additional fields required during user registration.
    """
    password: str
    company_id: Optional[int] = None
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None


class TeamMemberCreate(BaseModel):
    """
    Schema used for creating a new team member.
    
    Team members are always recruiters and inherit the company from the creator.
    """
    username: str
    email: EmailStr
    password: str
    profile_picture: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Schema used for updating an existing user.

    All fields are optional to allow partial updates.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    company_id: Optional[int] = None
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    """
    Schema used for returning user data in API responses.

    Includes nested company details and database-generated fields.
    """
    user_id: int
    profile_picture: Optional[str] = None
    created_at: datetime
    company: Optional[CompanyResponse] = None  # nested company

    model_config = {
        "from_attributes": True
    }