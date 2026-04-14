from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate


def create_interview(db: Session, data: InterviewCreate) -> Interview:
    """
    Create a new interview assignment between a user and an AI bot.

    Prevents duplicate assignments of the same user to the same bot.

    Args:
        db (Session): SQLAlchemy database session.
        data (InterviewCreate): Interview input data.

    Returns:
        Interview: Created interview object.

    Raises:
        ValueError: If the user is already assigned to the bot.
    """
    existing = (
        db.query(Interview)
        .filter(
            Interview.ai_bot_id == data.ai_bot_id,
            Interview.user_id == data.user_id,
        )
        .first()
    )

    if existing:
        raise ValueError("This user is already assigned to this bot")

    db_obj = Interview(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_interview(db: Session, bot_id: int, user_id: int) -> Interview | None:
    """
    Retrieve an interview by bot ID and user ID.

    Args:
        db (Session): SQLAlchemy database session.
        bot_id (int): AI Bot ID.
        user_id (int): User ID.

    Returns:
        Interview | None: Interview object if found, otherwise None.
    """
    return (
        db.query(Interview)
        .filter(
            Interview.ai_bot_id == bot_id,
            Interview.user_id == user_id,
        )
        .first()
    )


def update_interview(db: Session, bot_id: int, user_id: int, data: InterviewUpdate) -> Interview | None:
    """
    Update an existing interview.

    Args:
        db (Session): SQLAlchemy database session.
        bot_id (int): AI Bot ID.
        user_id (int): User ID.
        data (InterviewUpdate): Updated interview data.

    Returns:
        Interview | None: Updated interview object if found, otherwise None.
    """
    db_obj = get_interview(db, bot_id, user_id)
    if not db_obj:
        return None

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_interview(db: Session, bot_id: int, user_id: int) -> Interview | None:
    """
    Delete an interview by bot ID and user ID.

    Args:
        db (Session): SQLAlchemy database session.
        bot_id (int): AI Bot ID.
        user_id (int): User ID.

    Returns:
        Interview | None: Deleted interview object if found, otherwise None.
    """
    db_obj = get_interview(db, bot_id, user_id)
    if not db_obj:
        return None

    db.delete(db_obj)
    db.commit()
    return db_obj


def list_interviews(db: Session, skip: int = 0, limit: int = 100) -> list[Interview]:
    """
    Retrieve all interviews with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        list[Interview]: List of interview objects.
    """
    return db.query(Interview).offset(skip).limit(limit).all()