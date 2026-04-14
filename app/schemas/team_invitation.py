from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class TeamInvitationBase(BaseModel):
    """
    Base schema for Team Invitation.
    
    Contains common fields shared across invitation schemas.
    """
    invited_email: EmailStr


class TeamInvitationCreate(TeamInvitationBase):
    """
    Schema for creating a new team invitation.
    
    Used when a recruiter invites someone to join their team.
    """
    pass


class TeamInvitationResponse(TeamInvitationBase):
    """
    Schema for returning team invitation data in API responses.
    
    Includes all invitation details with timestamps.
    """
    invitation_id: str
    company_id: int
    invited_by: int
    status: str
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TeamInvitationUpdate(BaseModel):
    """
    Schema for updating team invitation status.
    
    Used for accepting, rejecting, or revoking invitations.
    """
    status: Optional[str] = None
    accepted_at: Optional[datetime] = None


class InvitationAcceptRequest(BaseModel):
    """
    Schema for accepting an invitation.
    
    Used when a user accepts an invitation via email link.
    """
    invitation_id: str


class InvitationAcceptResponse(BaseModel):
    """
    Response schema for invitation acceptance.
    
    Returns user details and company assignment.
    """
    message: str
    user_id: int
    company_id: int
    role: str
    company_name: str
