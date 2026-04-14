# app/repositories/job_application_repo.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.job_application import Job_Application
from app.models.user import User
from app.models.job import Job
from app.schemas.job_application import JobApplicationCreate


def create_job_application(db: Session, data: JobApplicationCreate) -> Job_Application:
    """
    Create a new job application after validating user and job existence.

    Args:
        db (Session): SQLAlchemy database session.
        data (JobApplicationCreate): Job application input data.

    Returns:
        Job_Application: Created job application object.

    Raises:
        ValueError: If user/job not found, duplicate application, or database error occurs.
    """
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        raise ValueError(f"User with id {data.user_id} not found")

    job = db.query(Job).filter(Job.job_id == data.job_id).first()
    if not job:
        raise ValueError(f"Job with id {data.job_id} not found")

    existing = db.query(Job_Application).filter(
        Job_Application.job_id == data.job_id,
        Job_Application.user_id == data.user_id
    ).first()

    if existing:
        raise ValueError("User already applied to this job")

    db_obj = Job_Application(**data.dict())
    try:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    except IntegrityError:
        db.rollback()
        raise ValueError("Database error while creating job application")

    return db_obj


def get_job_application(db: Session, job_id: int, user_id: int) -> Job_Application | None:
    """
    Retrieve a job application by job ID and user ID.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): Job ID.
        user_id (int): User ID.

    Returns:
        Job_Application | None: Application object if found, otherwise None.
    """
    return db.query(Job_Application).filter(
        Job_Application.job_id == job_id,
        Job_Application.user_id == user_id
    ).first()


def delete_job_application(db: Session, job_id: int, user_id: int) -> Job_Application | None:
    """
    Delete a job application by job ID and user ID.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): Job ID.
        user_id (int): User ID.

    Returns:
        Job_Application | None: Deleted object if found, otherwise None.
    """
    db_obj = get_job_application(db, job_id, user_id)
    if not db_obj:
        return None

    db.delete(db_obj)
    db.commit()
    return db_obj


def list_applications_by_job(db: Session, job_id: int) -> list[Job_Application]:
    """
    List all applications for a specific job.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): Job ID.

    Returns:
        list[Job_Application]: List of job applications.
    """
    return db.query(Job_Application).filter(
        Job_Application.job_id == job_id
    ).all()


def list_applications_by_user(db: Session, user_id: int) -> list[Job_Application]:
    """
    List all job applications made by a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): User ID.

    Returns:
        list[Job_Application]: List of job applications.
    """
    return db.query(Job_Application).filter(
        Job_Application.user_id == user_id
    ).all()


def list_job_applications(db: Session, skip: int = 0, limit: int = 100) -> list[Job_Application]:
    """
    Retrieve all job applications with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        list[Job_Application]: List of job applications.
    """
    return db.query(Job_Application).offset(skip).limit(limit).all()


def get_user_applications_query(db: Session, user_id: int):
    """
    Get base query for user's job applications.
    
    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): User ID to filter by.
        
    Returns:
        Query: Base query for user's applications.
    """
    return db.query(Job_Application).filter(Job_Application.user_id == user_id)


def get_company_applications_query(db: Session, company_id: int):
    """
    Get base query for company's job applications.
    
    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): Company ID to filter by.
        
    Returns:
        Query: Base query for company's applications.
    """
    return db.query(Job_Application).join(Job).filter(Job.company_id == company_id)