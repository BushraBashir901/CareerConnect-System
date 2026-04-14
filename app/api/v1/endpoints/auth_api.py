from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY
from app.models.user import User
from app.schemas.token_schema import TokenSchema, RefreshTokenRequest
from app.services.auth_service import (
    login_or_create_user,
    refresh_access_token,
    logout_user,
)
from app.core.auth import get_current_user
from app.core.oauth import (
    generate_state,
    verify_state,
    exchange_code_for_token,
    get_user_info
)
from app.core.dependency import get_db

import os

router = APIRouter(prefix="/auth", tags=["Authentication"])
BACKEND_URL = os.getenv("BACKEND_URL")


@router.get("/login/google")
def google_login(
    role: str = Query("candidate"),
):
    """
    Initiate Google OAuth login flow.

    Generates a state token for CSRF protection and returns the Google OAuth URL.

    Args:
        role (str): User role (candidate or recruiter).

    Returns:
        JSONResponse: Google OAuth URL for frontend redirection.

    Raises:
        HTTPException: If invalid role is provided.
    """
    if role not in ["candidate", "recruiter"]:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    # No company_id validation needed - recruiters get automatic company creation
    # Candidates never get company_id
    
    state = generate_state(role)

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&"
        f"redirect_uri={BACKEND_URL}/auth/google/callback&"
        f"scope=openid email profile&state={state}"
    )

    return JSONResponse(content={"url": google_auth_url})


@router.get("/google/callback")
def google_callback(
    code: str = Query(None, description="Authorization code from Google"),
    state: str = Query(None, description="CSRF state token"),
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.

    Exchanges authorization code for access token, fetches user info,
    and logs in or creates the user.

    Args:
        code (str): Authorization code from Google.
        state (str): CSRF state token.
        db (Session): Database session.

    Returns:
        JSONResponse: User data and JWT tokens.

    Raises:
        HTTPException: If authentication fails.
    """
    state_data = verify_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid state token")

    role = state_data.get("role", "candidate")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    access_token = exchange_code_for_token(
        code,
        f"{BACKEND_URL}/auth/google/callback"
    )

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    user_data = get_user_info(access_token)

    auth_result = login_or_create_user(db, user_data, role)

    return JSONResponse(content={
        "user": {
            "id": auth_result["user"].user_id,
            "username": auth_result["user"].username,
            "email": auth_result["user"].email,
            "role": auth_result["user"].role,
            "google_id": auth_result["user"].google_id,
            "is_active": auth_result["user"].is_active
        },
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    })


@router.post("/refresh", response_model=TokenSchema)
def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh JWT access token using a valid refresh token.

    Args:
        token_request (RefreshTokenRequest): Refresh token request body.
        db (Session): Database session.

    Returns:
        TokenSchema: New access and refresh tokens.

    Raises:
        HTTPException: If refresh token is invalid or expired.
    """
    token_data = refresh_access_token(db, token_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout the authenticated user.

    Revokes all refresh tokens for the current user.

    Args:
        current_user (User): Authenticated user.
        db (Session): Database session.

    Returns:
        dict: Logout confirmation message and revoked token count.
    """
    deleted = logout_user(db, current_user.user_id)

    return {
        "message": "Logged out successfully",
        "revoked_tokens": deleted
    }