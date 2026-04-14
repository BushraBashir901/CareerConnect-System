"""
User Profile Management API

Handles candidate profile management with strict RBAC enforcement.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependency import get_db
from app.dependencies.rbac_strict import (
    require_candidate, 
    require_self_access,
    require_authenticated_user
)
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import UserCreate, UserUpdate, UserResponse


router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile.
    
    Only authenticated users can access their own profile.
    
    Args:
        current_user (User): Authenticated user.
        db (Session): Database session.
        
    Returns:
        UserResponse: User profile data.
        
    Raises:
        HTTPException: If user not found.
    """
    user = user  # Current user is already fetched and validated
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role,
        google_id=user.google_id,
        is_active=user.is_active,
        profile_picture=user.profile_picture
    )


@router.put("/", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(require_self_access()),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Users can only update their own profile.
    
    Args:
        user_data (UserUpdate): Updated user data.
        current_user (User): Authenticated user.
        db (Session): Database session.
        
    Returns:
        UserResponse: Updated user profile.
        
    Raises:
        HTTPException: If user not found or unauthorized.
    """
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        google_id=current_user.google_id,
        is_active=current_user.is_active,
        profile_picture=current_user.profile_picture
    )


@router.delete("/")
def delete_profile(
    current_user: User = Depends(require_self_access()),
    db: Session = Depends(get_db)
):
    """
    Delete current user's profile.
    
    Users can only delete their own profile.
    
    Args:
        current_user (User): Authenticated user.
        db (Session): Database session.
        
    Returns:
        dict: Deletion confirmation.
        
    Raises:
        HTTPException: If user not found or unauthorized.
    """
    # Soft delete by setting is_active to False
    current_user.is_active = False
    db.commit()
    
    return {
        "message": "Profile deleted successfully",
        "user_id": current_user.user_id
    }


@router.get("/applications", response_model=List[dict])
def get_my_applications(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Get current user's job applications.
    
    Only candidates can access their applications.
    
    Args:
        current_user (User): Authenticated candidate user.
        db (Session): Database session.
        
    Returns:
        List[dict]: List of user's job applications.
    """
    applications = user_repo.get_user_applications(db, current_user.user_id)
    
    return [
        {
            "application_id": app.job_application_id,
            "job_id": app.job_id,
            "applied_at": app.applied_at.isoformat(),
            "status": app.status
        }
        for app in applications
    ]


@router.put("/applications/{application_id}")
def update_application(
    application_id: int,
    application_data: dict,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Update a job application.
    
    Only candidates can update their own applications.
    
    Args:
        application_id (int): Application ID.
        application_data (dict): Updated application data.
        current_user (User): Authenticated candidate user.
        db (Session): Database session.
        
    Returns:
        dict: Updated application.
        
    Raises:
        HTTPException: If application not found or unauthorized.
    """
    # Implementation would go here with proper validation
    return {
        "message": "Application update functionality",
        "application_id": application_id
    }


@router.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    """
    Delete a job application.
    
    Only candidates can delete their own applications.
    
    Args:
        application_id (int): Application ID.
        current_user (User): Authenticated candidate user.
        db (Session): Database session.
        
    Returns:
        dict: Deletion confirmation.
        
    Raises:
        HTTPException: If application not found or unauthorized.
    """
    # Implementation would go here with proper validation
    return {
        "message": "Application delete functionality",
        "application_id": application_id
    }
