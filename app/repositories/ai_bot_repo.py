# app/repositories/ai_bot_repo.py
from sqlalchemy.orm import Session
from app.models.ai_bot import AiBot
from app.schemas.ai_bot import AiBotCreate, AiBotUpdate


def create_ai_evaluation(db: Session, evaluation: AiBotCreate) -> AiBot:
    """
    Create a new AI bot evaluation record.

    Args:
        db (Session): SQLAlchemy database session.
        evaluation (AiBotCreate): AI bot input data.

    Returns:
        AiBot: Created AI bot record.
    """
    db_evaluation = AiBot(**evaluation.dict(exclude={"bot_id"}))  # Exclude auto-generated primary key
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def get_ai_evaluation(db: Session, evaluation_id: int) -> AiBot | None:
    """
    Retrieve an AI bot evaluation by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        evaluation_id (int): AI bot ID.

    Returns:
        AiBot | None: AI bot object if found, otherwise None.
    """
    return db.query(AiBot).filter(AiBot.bot_id == evaluation_id).first()


def update_ai_evaluation(db: Session, evaluation_id: int, evaluation: AiBotUpdate) -> AiBot | None:
    """
    Update an existing AI bot evaluation.

    Args:
        db (Session): SQLAlchemy database session.
        evaluation_id (int): AI bot ID.
        evaluation (AiBotUpdate): Updated data.

    Returns:
        AiBot | None: Updated AI bot object if found, otherwise None.
    """
    db_evaluation = get_ai_evaluation(db, evaluation_id)
    if not db_evaluation:
        return None

    update_data = evaluation.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_evaluation, key, value)

    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def delete_ai_evaluation(db: Session, evaluation_id: int) -> AiBot | None:
    """
    Delete an AI bot evaluation by ID.

    Args:
        db (Session): SQLAlchemy database session.
        evaluation_id (int): AI bot ID.

    Returns:
        AiBot | None: Deleted AI bot object if found, otherwise None.
    """
    db_evaluation = get_ai_evaluation(db, evaluation_id)
    if not db_evaluation:
        return None

    db.delete(db_evaluation)
    db.commit()
    return db_evaluation


def list_ai_evaluations(db: Session, skip: int = 0, limit: int = 100) -> list[AiBot]:
    """
    Retrieve all AI bot evaluations with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        list[AiBot]: List of AI bot records.
    """
    return db.query(AiBot).offset(skip).limit(limit).all()