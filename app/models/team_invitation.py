from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import enum

from app.db.base_class import Base


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class TeamInvitation(Base):
    """
    Team invitation model for email-based team member invitations.
    
    Allows company admins to invite team members via email.
    When accepted, users automatically get recruiter role and company assignment.
    """
    __tablename__ = "team_invitations"
    
    invitation_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    invited_email = Column(String(255), nullable=False, index=True)
    invited_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Status and timing
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7), nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="team_invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<TeamInvitation(id={self.invitation_id}, email={self.invited_email}, status={self.status})>"
    
    @property
    def is_expired(self):
        """Check if invitation has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if invitation is valid for acceptance."""
        return self.status == InvitationStatus.PENDING and not self.is_expired
