from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.token_schema import TokenSchema, RefreshTokenRequest
from app.services.auth_service import (
    autheticate,
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
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])
BACKEND_URL = settings.BACKEND_URL


@router.get("/login/google")
def google_login(
    role: str | None = Query(),
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
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={BACKEND_URL}/auth/google/callback&"
        f"scope=openid email profile&state={state}"
    )

    return JSONResponse(content={"url": google_auth_url})
    
    #return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
def google_callback(
    code: str = Query(None, description="Authorization code from Google"),
    state: str = Query(None, description="CSRF state token"),
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback and authenticate user.
    
    Exchanges authorization code for access token, retrieves user info,
    and authenticates/creates user in the system.
    
    Args:
        code: Authorization code received from Google OAuth
        state: CSRF state token for security validation
        db: Database session dependency
        
    Returns:
        JSONResponse: User data with access tokens and role information
        
    Raises:
        HTTPException: If state token invalid, code missing, or token exchange fails
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
    auth_result = autheticate(db, user_data, role)

    user = auth_result["user"]

    safe_role = (
        list(user.role)[0] if isinstance(user.role, set) else user.role
    )

    safe_message = (
        list(auth_result.get("message"))[0]
        if isinstance(auth_result.get("message"), set)
        else auth_result.get("message", "")
    )

    return JSONResponse(content={
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": safe_role,  
            "google_id": user.google_id,
            "is_active": user.is_active
        },
        "access_token": auth_result["access_token"],
        "token_type": "bearer",
        "message": safe_message  
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