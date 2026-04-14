from pydantic import BaseModel
from typing import Optional


class TokenSchema(BaseModel):
    """
    Schema for authentication tokens returned to the client.

    Attributes:
        access_token (str): JWT access token.
        refresh_token (Optional[str]): Refresh token used to generate new access tokens.
        token_type (str): Type of token (default is 'bearer').
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token API request.

    Attributes:
        refresh_token (str): Refresh token provided by the client.
    """
    refresh_token: str


class LogoutRequest(BaseModel):
    """
    Schema for logout request.

    Attributes:
        refresh_token (Optional[str]): Refresh token to be revoked during logout.
    """
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """
    Schema representing decoded JWT token payload.

    Attributes:
        sub (int): User ID (subject of token).
        role (str): Role of the user.
        exp (int): Expiration timestamp of the token.
    """
    sub: int  # user_id
    role: str
    exp: int