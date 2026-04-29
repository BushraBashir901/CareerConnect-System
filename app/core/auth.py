from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.models.user import User
from app.core.security import decode_jwt

# Security scheme
security = HTTPBearer()

class CurrentUser:
    """
    Extracts and validates JWT token, returns the current user.
    """
    def __init__(self, credentials: HTTPAuthorizationCredentials = Depends(security),
                 db: Session = Depends(get_db)):
        self.credentials = credentials
        self.db = db
        self.user = self._get_user()

    # Internal method to decode JWT and fetch user from DB
    def _get_user(self) -> User:
        token = self.credentials.credentials
        payload = decode_jwt(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        return user


def verify_token(token: str):
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    return decode_jwt(token)


async def get_current_user(current_user: CurrentUser = Depends()) -> User:
    """
    FastAPI dependency to get the authenticated user.
    Usage: def endpoint(current_user: User = Depends(get_current_user))
    """
    return current_user.user