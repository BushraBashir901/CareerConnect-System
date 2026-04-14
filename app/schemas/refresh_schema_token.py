from pydantic import BaseModel


class RefreshTokenCreate(BaseModel):
    """
    Schema used to create a new refresh token.

    Attributes:
        user_id (int): ID of the user the token belongs to.
        token (str): Refresh token string.
        expires_at (str): Expiration datetime in ISO format.
    """
    user_id: int
    token: str
    expires_at: str  # ISO datetime


class RefreshTokenResponse(BaseModel):
    """
    Schema used for returning refresh token data in API responses.

    Attributes:
        id (int): Database ID of the refresh token.
        user_id (int): ID of the user the token belongs to.
        token (str): Refresh token string.
        expires_at (str): Expiration datetime in ISO format.
    """
    id: int
    user_id: int
    token: str
    expires_at: str

    class Config:
        orm_mode = True