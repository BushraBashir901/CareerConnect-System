from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db (Session): SQLAlchemy database session.
        user_data (UserCreate): User input data.

    Returns:
        User: The created user object.
    
    """
    existing_user = db.query(User).filter(User.email == User.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,  # hash in service layer
        role=user_data.role,
        profile_picture=user_data.profile_picture,
        is_active=user_data.is_active,
        company_id=user_data.company_id,
        google_id=user_data.google_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(db: Session, user_id: int) -> User | None:
    """
    Retrieve a user by user ID.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user.

    Returns:
        User | None: User object if found, otherwise None.
    """
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by email.

    Args:
        db (Session): SQLAlchemy database session.
        email (str): User email.

    Returns:
        User | None: User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User | None:
    """
    Update an existing user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user to update.
        user_data (UserUpdate): Updated user data.

    Returns:
        User | None: Updated user object if found, otherwise None.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> User | None:
    """
    Delete a user from the database.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user to delete.

    Returns:
        User | None: Deleted user object if found, otherwise None.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Retrieve a list of users with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of users to return.

    Returns:
        list[User]: List of user objects.
    """
    return db.query(User).offset(skip).limit(limit).all()


def list_users_by_company(db: Session, company_id: int) -> list[User]:
    """
    Retrieve a list of users belonging to a specific company.

    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): Company ID to filter users by.

    Returns:
        list[User]: List of user objects belonging to the company.
    """
    return db.query(User).filter(
        User.company_id == company_id,
        User.is_active == True
    ).all()