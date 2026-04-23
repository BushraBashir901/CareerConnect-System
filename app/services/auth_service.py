import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.company import Company
from app.core.rbac import RoleEnum
from app.core.security import create_jwt
from app.core.config import settings
from fastapi import HTTPException
from app.repositories.token_repo import (
    create_refresh_token,
    get_refresh_token,
    delete_refresh_token,
)


GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
BACKEND_URL = settings.BACKEND_URL

# Temporary state store (replace with Redis for production)
state_store = {}


def autheticate(db: Session, user_info: dict, role: str | None = None):
    """
    Authenticates a user with Google OAuth and creates/updates their record.
    
    Args:
        db (Session): SQLAlchemy database session.
        user_info (dict): User information from Google OAuth.
        role (str | None): Role to assign to the user.
        company_id (int): Company ID for recruiter users.
    
    Returns:
        dict: Contains 'user', 'access_token', and 'refresh_token'.
    """
    # Check if user already exists
    user = db.query(User).filter(User.email == user_info["email"]).first()
    message = {"Gmail already exist"}

    if user:
        if user.role:
            # Only warn if user is TRYING to change role
            if role is not None and role != user.role:
                message = "Role already assigned. Please update it in settings."

        elif role:
            user.role = role
            db.commit()

    else:
        role = role if role is not None else "candidate"
    
    return login_or_create_user(db, user_info, role, message , user)


        
def login_or_create_user(db: Session, user_info: dict, role: str | None = None, message: str = None , user: User = None) -> dict:
    """
    Logs in an existing user or creates a new one if they do not exist.

    Generates access and refresh tokens and stores the refresh token in the database.

    Args:
        db (Session): SQLAlchemy database session.
        user_info (dict): User information obtained from Google OAuth.
        role (str): Role assigned to the user.

    Returns:
        dict: Contains 'user', 'access_token', and 'refresh_token'.
    """

    # Create user if not exists
    if not user:
        user_company_id = None
        
        # Automatic company creation for recruiters on first login
        if role == "recruiter":
            # Create a new company for the recruiter
            company_name = f"{user_info.get('name', 'Unknown')}'s Company"
            new_company = Company(
                company_name=company_name,
                description=f"Company for {user_info.get('name', 'Unknown')}"
            )
            db.add(new_company)
            db.commit()
            db.refresh(new_company)
            
            # Link recruiter to the new company
            user_company_id = new_company.company_id
            
        elif role == "candidate":
            # Candidates never get a company_id
            user_company_id = None
        
        user = User(
            username=user_info.get("name"),
            email=user_info["email"],
            google_id=user_info.get("id"), 
            role=role,  
            company_id=user_company_id, 
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate access token
    access_token = create_jwt(user.user_id, user.role, expires_minutes=60)

    # Create refresh token using repository
    create_refresh_token(db, user.user_id)

    return {
        "user": user,
        "access_token": access_token,
        "message": message,
    }


def refresh_access_token(db: Session, refresh_token_str: str) -> dict | None:
    """
    Validates a refresh token and rotates it if valid.

    Returns a new access token and a rotated refresh token.

    Args:
        db (Session): SQLAlchemy database session.
        refresh_token_str (str): Refresh token string sent by the client.

    Returns:
        dict | None: New access token and refresh token if valid, otherwise None.
    """
    refresh_token = get_refresh_token(db, refresh_token_str)

    if not refresh_token:
        return None

    if refresh_token.expires_at and refresh_token.expires_at < datetime.utcnow():
        delete_refresh_token(db, refresh_token)
        db.commit()
        return None

    user = db.query(User).filter(User.user_id == refresh_token.user_id).first()

    if not user or not user.is_active:
        return None

    delete_refresh_token(db, refresh_token)

    new_refresh_token_obj = create_refresh_token(db, user.user_id)

    access_token = create_jwt(user.user_id, user.role, expires_minutes=60)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_obj.token,
    }


def revoke_user_refresh_tokens(db: Session, user_id: int) -> int:
    """
    Revokes all refresh tokens for a given user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user whose tokens should be revoked.

    Returns:
        int: Number of deleted tokens.
    """
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).all()

    deleted_count = len(tokens)

    for token in tokens:
        delete_refresh_token(db, token)

    if deleted_count:
        db.commit()

    return deleted_count


def logout_user(db: Session, user_id: int):
    """
    Logs out a user by revoking all their refresh tokens.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user logging out.

    Returns:
        int: Number of revoked tokens.
    """
    return revoke_user_refresh_tokens(db, user_id)