from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.team_invitation import TeamInvitation, InvitationStatus
from app.models.company import Company
from app.utils.pagination import paginate_query, create_paginated_response


def create_team_invitation(db: Session, invitation_data: dict) -> TeamInvitation:
    """
    Create a new team invitation.
    
    Args:
        db: Database session
        invitation_data: Dictionary with invitation details
        
    Returns:
        Created TeamInvitation object
    """
    invitation = TeamInvitation(**invitation_data)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


def get_invitation_by_id(db: Session, invitation_id: str) -> Optional[TeamInvitation]:
    """
    Get team invitation by ID.
    
    Args:
        db: Database session
        invitation_id: Invitation ID
        
    Returns:
        TeamInvitation object or None
    """
    return db.query(TeamInvitation).filter(
        TeamInvitation.invitation_id == invitation_id
    ).first()


def get_invitation_by_email_and_company(db: Session, email: str, company_id: int) -> Optional[TeamInvitation]:
    """
    Get pending invitation by email and company.
    
    Args:
        db: Database session
        email: Email address
        company_id: Company ID
        
    Returns:
        TeamInvitation object or None
    """
    return db.query(TeamInvitation).filter(
        and_(
            TeamInvitation.invited_email == email,
            TeamInvitation.company_id == company_id,
            TeamInvitation.status == InvitationStatus.PENDING,
            TeamInvitation.expires_at > datetime.utcnow()
        )
    ).first()


def get_company_invitations(db: Session, company_id: int, offset: int = 0, limit: int = 20) -> tuple:
    """
    Get paginated invitations for a company.
    
    Args:
        db: Database session
        company_id: Company ID
        offset: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (invitations_list, total_count)
    """
    query = db.query(TeamInvitation).filter(
        TeamInvitation.company_id == company_id
    ).order_by(TeamInvitation.created_at.desc())
    
    return paginate_query(query, offset, limit)


def get_company_invitations_unpaginated(db: Session, company_id: int) -> List[TeamInvitation]:
    """
    Get all invitations for a company (unpaginated version).
    
    Args:
        db: Database session
        company_id: Company ID
        
    Returns:
        List of TeamInvitation objects
    """
    return db.query(TeamInvitation).filter(
        TeamInvitation.company_id == company_id
    ).order_by(TeamInvitation.created_at.desc()).all()


def accept_invitation(db: Session, invitation_id: str) -> Optional[TeamInvitation]:
    """
    Accept a team invitation.
    
    Args:
        db: Database session
        invitation_id: Invitation ID
        
    Returns:
        Updated TeamInvitation object or None
    """
    invitation = get_invitation_by_id(db, invitation_id)
    
    if not invitation or not invitation.is_valid:
        return None
    
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(invitation)
    return invitation


def revoke_invitation(db: Session, invitation_id: str, company_id: int) -> Optional[TeamInvitation]:
    """
    Revoke a team invitation.
    
    Args:
        db: Database session
        invitation_id: Invitation ID
        company_id: Company ID (for security)
        
    Returns:
        Updated TeamInvitation object or None
    """
    invitation = db.query(TeamInvitation).filter(
        and_(
            TeamInvitation.invitation_id == invitation_id,
            TeamInvitation.company_id == company_id
        )
    ).first()
    
    if not invitation:
        return None
    
    invitation.status = InvitationStatus.REVOKED
    db.commit()
    db.refresh(invitation)
    return invitation


def cleanup_expired_invitations(db: Session) -> int:
    """
    Mark expired invitations as expired.
    
    Args:
        db: Database session
        
    Returns:
        Number of invitations marked as expired
    """
    expired_count = db.query(TeamInvitation).filter(
        and_(
            TeamInvitation.status == InvitationStatus.PENDING,
            TeamInvitation.expires_at < datetime.utcnow()
        )
    ).update(
        {TeamInvitation.status: InvitationStatus.EXPIRED},
        synchronize_session=False
    )
    
    db.commit()
    return expired_count


def check_existing_user_invitation(db: Session, email: str, company_id: int) -> bool:
    """
    Check if user already has a pending invitation for this company.
    
    Args:
        db: Database session
        email: Email address
        company_id: Company ID
        
    Returns:
        True if pending invitation exists, False otherwise
    """
    invitation = get_invitation_by_email_and_company(db, email, company_id)
    return invitation is not None
