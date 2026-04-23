from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.company import Company
from app.schemas.job import JobCreate, JobUpdate
from app.services.embeddings_service import generate_embedding


def create_job(db: Session, job_data: JobCreate, company_id: int) -> Job:
    """
    Create a new job in the database after validating the company exists.
    """

    company = db.query(Company).filter(
        Company.company_id == company_id
    ).first()

    if not company:
        raise ValueError(f"Company with id {company_id} not found")

    # Generate embedding from job description
    embedding = generate_embedding(job_data.job_description)

    db_job = Job(
        **job_data.dict(),
        company_id=company_id,
        embedding=embedding
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job(db: Session, job_id: int) -> Job | None:
    """
    Retrieve a job by job ID.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): ID of the job.

    Returns:
        Job | None: Job object if found, otherwise None.
    """
    return db.query(Job).filter(Job.job_id == job_id).first()


def update_job(db: Session, job_id: int, job_data: JobUpdate) -> Job | None:
    """
    Update an existing job.

    Validates company if company_id is updated.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): ID of the job to update.
        job_data (JobUpdate): Updated job data.

    Returns:
        Job | None: Updated job object if found, otherwise None.

    Raises:
        ValueError: If updated company_id does not exist.
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None

    update_data = job_data.dict(exclude_unset=True)

    # Validate company if updated
    if "company_id" in update_data:
        company = db.query(Company).filter(
            Company.company_id == update_data["company_id"]
        ).first()

        if not company:
            raise ValueError(f"Company with id {update_data['company_id']} not found")

    for field, value in update_data.items():
        setattr(db_job, field, value)

    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: int) -> Job | None:
    """
    Delete a job from the database.

    Args:
        db (Session): SQLAlchemy database session.
        job_id (int): ID of the job to delete.

    Returns:
        Job | None: Deleted job object if found, otherwise None.
    """
    db_job = get_job(db, job_id)
    if not db_job:
        return None

    db.delete(db_job)
    db.commit()
    return db_job


def get_all_jobs_query(db: Session):
    """
    Get query for all jobs (for candidates).
    
    Args:
        db (Session): SQLAlchemy database session.
        
    Returns:
        Query object for all jobs.
    """
    return db.query(Job)


def get_company_jobs_query(db: Session, company_id: int):
    """
    Get query for jobs filtered by company (for recruiters).
    
    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): Company ID to filter by.
        
    Returns:
        Query object for company jobs.
    """
    return db.query(Job).filter(Job.company_id == company_id)


def list_jobs(db: Session, skip: int = 0, limit: int = 100) -> list[Job]:
    """
    Retrieve a list of jobs with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of jobs to return.

    Returns:
        list[Job]: List of job objects.
    """
    return db.query(Job).offset(skip).limit(limit).all()