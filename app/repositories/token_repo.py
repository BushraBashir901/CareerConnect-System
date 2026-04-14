from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


def create_refresh_token(db: Session, user_id: int) -> RefreshToken:
    """
    Create a new refresh token for the given user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): The ID of the user.

    Returns:
        RefreshToken: The created refresh token object.
    """
    import secrets

    refresh_token_str = secrets.token_urlsafe(32)
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token(db: Session, token: str) -> RefreshToken | None:
    """
    Retrieve a refresh token by its token string.

    Args:
        db (Session): SQLAlchemy database session.
        token (str): The refresh token string.

    Returns:
        RefreshToken | None: The refresh token object if found, None otherwise.
    """
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def delete_refresh_token(db: Session, token_obj: RefreshToken) -> None:
    """
    Delete a refresh token from the database.

    Args:
        db (Session): SQLAlchemy database session.
        token_obj (RefreshToken): The refresh token object to delete.
    """
    db.delete(token_obj)
    # Note: Commit is handled by the service layer for flexibility