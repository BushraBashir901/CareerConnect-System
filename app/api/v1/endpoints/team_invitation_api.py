from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from task.send_email_invitation_task import send_team_invitation_email


from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.models.company import Company
from app.repositories import team_invitation_repo, company_repo
from app.schemas.team_invitation import (
    TeamInvitationCreate, TeamInvitationResponse, 
    InvitationAcceptResponse
)
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import create_paginated_response

router = APIRouter(
    prefix="/team-invitations",
    tags=["Team Invitations"]
)


@router.post("/", response_model=TeamInvitationResponse, status_code=status.HTTP_201_CREATED)
def send_team_invitation(
    invitation: TeamInvitationCreate,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
):
    """
    Send a team invitation to an email address.
    
    Requires MANAGE_TEAM_MEMBERS permission.
    Only company admins can send invitations.
    """
    current_user, db = auth_data
    
    # Get current user's company
    company = company_repo.get_company_by_user(db, current_user.user_id)
    if not company:
        raise HTTPException(
            status_code=400,
            detail="No company assigned to this user"
        )
    
    # Check if invitation already exists
    existing_invitation = team_invitation_repo.get_invitation_by_email_and_company(
        db, invitation.invited_email, company.company_id
    )
    if existing_invitation:
        raise HTTPException(
            status_code=400,
            detail="Invitation already sent to this email for this company"
        )
    
    # Create invitation
    invitation_data = {
        "company_id": company.company_id,
        "invited_email": invitation.invited_email,
        "invited_by": current_user.user_id
    }
    
    team_invitation = team_invitation_repo.create_team_invitation(db, invitation_data)
    
    # Send email invitation asynchronously->background task
    send_team_invitation_email.delay(
        to_email=invitation.invited_email,
        inviter_name=current_user.username,
        company_name=company.company_name,
        invitation_id=team_invitation.invitation_id,
        expires_at=team_invitation.expires_at
    )
    
    return team_invitation


@router.get("/", response_model=PaginatedResponse[TeamInvitationResponse])
def list_company_invitations(
    pagination: PaginationParams = Depends(),
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
):
    """
    List paginated invitations for the current user's company.
    
    Supports offset-based pagination for performance.
    
    Query Parameters:
        offset: Number of items to skip (default: 0)
        limit: Maximum items per page (default: 20, max: 100)
    
    Requires MANAGE_TEAM_MEMBERS permission.
    """
    current_user, db = auth_data
    
    # Get current user's company
    company = company_repo.get_company_by_user(db, current_user.user_id)
    if not company:
        raise HTTPException(
            status_code=400,
            detail="No company assigned to this user"
        )
    
    # Get paginated invitations
    invitations, total = team_invitation_repo.get_company_invitations(
        db, company.company_id, pagination.offset, pagination.limit
    )
    
    return create_paginated_response(
        items=invitations,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
        page_class=TeamInvitationResponse
    )


@router.post("/accept/{invitation_id}", response_model=InvitationAcceptResponse)
def accept_invitation(
    invitation_id: str,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.CREATE_APPLICATIONS)),
):
    """
    Accept a team invitation.
    
    This endpoint is called after user authentication (Google OAuth).
    Links the user to the company and assigns recruiter role.
    """
    current_user, db = auth_data
    
    # Get invitation
    invitation = team_invitation_repo.get_invitation_by_id(db, invitation_id)
    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
        )
    
    # Validate invitation
    if not invitation.is_valid:
        if invitation.status == "accepted":
            raise HTTPException(
                status_code=400,
                detail="Invitation has already been accepted"
            )
        elif invitation.is_expired:
            raise HTTPException(
                status_code=400,
                detail="Invitation has expired"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invitation is no longer valid"
            )
    
    # Verify email matches
    if current_user.email.lower() != invitation.invited_email.lower():
        raise HTTPException(
            status_code=403,
            detail="This invitation was sent to a different email address"
        )
    
    # Accept invitation
    accepted_invitation = team_invitation_repo.accept_invitation(db, invitation_id)
    if not accepted_invitation:
        raise HTTPException(
            status_code=500,
            detail="Failed to accept invitation"
        )
    
    # Update user role and company
    current_user.role = "recruiter"
    current_user.company_id = invitation.company_id
    db.commit()
    
    # Get company details
    company = db.query(Company).filter(Company.company_id == invitation.company_id).first()
    
    return InvitationAcceptResponse(
        message="Successfully joined the team!",
        user_id=current_user.user_id,
        company_id=invitation.company_id,
        role=current_user.role,
        company_name=company.company_name if company else "Unknown"
    )


@router.delete("/{invitation_id}", response_model=TeamInvitationResponse)
def revoke_invitation(
    invitation_id: str,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
):
    """
    Revoke a team invitation.
    
    Requires MANAGE_TEAM_MEMBERS permission.
    Only company admins can revoke invitations.
    """
    current_user, db = auth_data
    
    # Get current user's company
    company = company_repo.get_company_by_user(db, current_user.user_id)
    if not company:
        raise HTTPException(
            status_code=400,
            detail="No company assigned to this user"
        )
    
    # Revoke invitation
    revoked_invitation = team_invitation_repo.revoke_invitation(
        db, invitation_id, company.company_id
    )
    
    if not revoked_invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found or you don't have permission to revoke it"
        )
    
    return revoked_invitation


@router.get("/public/{invitation_id}")
def get_public_invitation_info(invitation_id: str, db: Session = Depends(get_db)):
    """
    Get public invitation information.
    
    This endpoint is accessible without authentication for invitation validation.
    Used to show invitation details before user authentication.
    """
    invitation = team_invitation_repo.get_invitation_by_id(db, invitation_id)
    
    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
        )
    
    if not invitation.is_valid:
        if invitation.status == "accepted":
            raise HTTPException(
                status_code=400,
                detail="Invitation has already been accepted"
            )
        elif invitation.is_expired:
            raise HTTPException(
                status_code=400,
                detail="Invitation has expired"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invitation is no longer valid"
            )
    
    # Return limited public information
    return {
        "invitation_id": invitation.invitation_id,
        "invited_email": invitation.invited_email,
        "company_name": invitation.company.company_name if invitation.company else "Unknown Company",
        "expires_at": invitation.expires_at,
        "inviter_name": invitation.inviter.username if invitation.inviter else "Unknown"
    }
