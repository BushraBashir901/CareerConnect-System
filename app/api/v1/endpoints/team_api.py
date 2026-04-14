from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.models.user import User
from app.schemas.user import TeamMemberCreate, UserResponse
from app.core.security import hash_password
from app.repositories import user_repo

router = APIRouter(prefix="/team", tags=["Team Management"])


# -------------------------
# Add Team Member
# -------------------------
@router.post("/members", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    member_data: TeamMemberCreate,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
):
    current_user, db = auth_data
    """
    Add a new team member to the recruiter's company.
    
    Only recruiters can add team members to their own company.
    The new member will be automatically linked to the recruiter's company.
    
    Args:
        member_data (UserCreate): Team member data including email and password.
        current_user (User): Authenticated recruiter user.
        db (Session): Database session.
    
    Returns:
        UserResponse: Created team member information.
    
    Raises:
        HTTPException: If user already exists or validation fails.
    """
    # Ensure current user is a recruiter
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can add team members"
        )
    
    # Check if user already exists
    existing_user = user_repo.get_user_by_email(db, member_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new team member with recruiter's company
    hashed_password = hash_password(member_data.password)
    new_member = User(
        username=member_data.username,
        email=member_data.email,
        password=hashed_password,
        role="recruiter",  # All team members are recruiters
        company_id=current_user.company_id,  # Link to recruiter's company
        is_active=True
    )
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member


# -------------------------
# List Team Members
# -------------------------
@router.get("/members", response_model=List[UserResponse])
def list_team_members(
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_TEAM_MEMBERS)),
):
    current_user, db = auth_data
    """
    List all team members in the recruiter's company.
    
    Args:
        current_user (User): Authenticated recruiter user.
        db (Session): Database session.
    
    Returns:
        List[UserResponse]: List of team members.
    
    Raises:
        HTTPException: If user is not a recruiter or has no company.
    """
    # Ensure current user is a recruiter
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view team members"
        )
    
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recruiter must belong to a company"
        )
    
    # Get all users in the same company
    team_members = db.query(User).filter(
        User.company_id == current_user.company_id,
        User.is_active == True
    ).all()
    
    return team_members


# -------------------------
# Remove Team Member
# -------------------------
@router.delete("/members/{member_id}", response_model=UserResponse)
def remove_team_member(
    member_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
):
    current_user, db = auth_data
    """
    Remove a team member from the company.
    
    Only recruiters can remove team members from their own company.
    Cannot remove yourself.
    
    Args:
        member_id (int): ID of the team member to remove.
        current_user (User): Authenticated recruiter user.
        db (Session): Database session.
    
    Returns:
        UserResponse: Removed team member information.
    
    Raises:
        HTTPException: If member not found or validation fails.
    """
    # Ensure current user is a recruiter
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can remove team members"
        )
    
    # Cannot remove yourself
    if member_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the team"
        )
    
    # Get the team member to remove
    team_member = db.query(User).filter(User.user_id == member_id).first()
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Ensure the team member belongs to the same company
    if team_member.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove team member from different company"
        )
    
    # Deactivate the team member (soft delete)
    team_member.is_active = False
    db.commit()
    
    return JSONResponse({"message": "Team member removed successfully"})
