"""
Role-Based Protected Routes Examples

Demonstrates strict RBAC enforcement for each role.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
#from typing import List

from app.core.dependency import get_db
from app.dependencies.rbac_strict import (
    #require_admin,
    require_recruiter,
    require_candidate,
    require_any_role,
    require_company_membership,
    require_self_access,
    require_authenticated_user
)
from app.core.rbac import RoleEnum, PermissionEnum
from app.models.user import User
from app.repositories import company_repo# , job_repo


router = APIRouter(prefix="/examples", tags=["Role Examples"])


# -------------------------
# Recruiter Only Routes
# -------------------------
@router.get("/recruiter-dashboard")
def recruiter_dashboard(
    current_user: User = Depends(require_recruiter()),
    db: Session = Depends(get_db)
):
    """
    Recruiter dashboard - Recruiters only.
    
    Demonstrates recruiter-only access with company membership validation.
    """
    company = company_repo.get_company_by_user(db, current_user.user_id)
    
    return {
        "message": "Welcome to Recruiter Dashboard",
        "user": current_user.username,
        "company": company.company_name if company else "No company assigned"
    }


@router.get("/recruiter-jobs")
def recruiter_jobs(
    current_user: User = Depends(require_company_membership()),
    db: Session = Depends(get_db)
):
    """
    View company jobs - Recruiters only.
    
    Demonstrates company-scoped access for recruiters.
    """
    company = company_repo.get_company_by_user(db, current_user.user_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter must belong to a company"
        )
    
    # Implementation would fetch jobs for this company only
    return {
        "message": "Jobs for your company",
        "company": company.company_name,
        "company_id": company.company_id
    }


# -------------------------
# Candidate Only Routes
# -------------------------
@router.get("/candidate-dashboard")
def candidate_dashboard(
    current_user: User = Depends(require_candidate()),
    db: Session = Depends(get_db)
):
    """
    Candidate dashboard - Candidates only.
    
    Demonstrates candidate-only access control.
    """
    return {
        "message": "Welcome to Candidate Dashboard",
        "user": current_user.username,
        "role": current_user.role,
        "company_id": current_user.company_id  # Should be None for candidates
    }


@router.get("/my-applications")
def candidate_applications(
    current_user: User = Depends(require_self_access()),
    db: Session = Depends(get_db)
):
    """
    View my applications - Candidates only.
    
    Demonstrates self-access pattern for candidates.
    """
    return {
        "message": "Your job applications",
        "user_id": current_user.user_id,
        "can_only_access_own": True
    }


# -------------------------
# Multi-Role Routes
# -------------------------
@router.get("/shared-dashboard")
def shared_dashboard(
    current_user: User = Depends(require_any_role([
        RoleEnum.ADMIN, 
        RoleEnum.RECRUITER, 
        RoleEnum.CANDIDATE
    ])),
    db: Session = Depends(get_db)
):
    """
    Shared dashboard - All authenticated users.
    
    Demonstrates multi-role access control.
    """
    return {
        "message": f"Welcome {current_user.username}",
        "role": current_user.role,
        "access_level": "Authenticated user"
    }


@router.get("/profile")
def user_profile(
    current_user: User = Depends(require_authenticated_user()),
    db: Session = Depends(get_db)
):
    """
    User profile - Any authenticated user.
    
    Demonstrates basic authentication requirement.
    """
    return {
        "message": "User Profile",
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


# -------------------------
# Permission Examples
# -------------------------
@router.get("/permission-demo/{permission}")
def permission_demo(
    permission: str,
    current_user: User = Depends(require_authenticated_user()),
    db: Session = Depends(get_db)
):
    """
    Permission-based access demonstration.
    
    Shows how to check specific permissions.
    """
    # Map string to permission enum
    permission_map = {
        "manage_users": PermissionEnum.MANAGE_USERS,
        "create_jobs": PermissionEnum.CREATE_JOBS,
        "view_applications": PermissionEnum.VIEW_APPLICATIONS,
        "run_ai": PermissionEnum.RUN_AI_EVALUATION,
    }
    
    if permission not in permission_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid permission specified"
        )
    
    required_permission = permission_map[permission]
    
    # Check if user has this permission
    from app.core.rbac import has_permission
    user_role = RoleEnum(current_user.role)
    
    has_perm = has_permission(user_role, required_permission)
    
    return {
        "message": f"Permission check for {permission}",
        "user_role": current_user.role,
        "required_permission": required_permission.value,
        "has_permission": has_perm,
        "access_granted": has_perm
    }
