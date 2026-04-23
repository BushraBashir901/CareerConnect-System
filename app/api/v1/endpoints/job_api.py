# app/api/job_api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.core.dependency import get_db
from app.core.rbac import PermissionEnum, RoleEnum
from app.dependencies.rbac_strict import (
    require_permission_with_company_scope, 
    require_company_ownership, 
    require_admin_or_company_owner
)
from app.repositories import (
    job_repo, 
    company_repo
)
from app.schemas.job import (
    JobCreate, 
    JobUpdate, 
    JobResponse
)
from app.schemas.pagination import(
    PaginationParams,
    PaginatedResponse
)
from app.utils.pagination import(
     paginate_query, 
     create_paginated_response
)
from app.utils.filtering import(
    JobFilterParams, 
    apply_job_filters
)



router = APIRouter(prefix="/jobs", tags=["Jobs"])


# -------------------------
# Create Job
# -------------------------
@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.CREATE_JOBS)),
):
    current_user, db = auth_data
    """
    Create job and attach company_id automatically.
    """
    # 1. Find company of this recruiter/user
    company = company_repo.get_company_by_user(db, current_user.user_id)

    if not company:
        raise HTTPException(
            status_code=400,
            detail="No company assigned to this user"
        )

    # 2. Create job with company_id (passed separately)
    try:
        return job_repo.create_job(db, job, company.company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Get Job by ID
# -------------------------
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_JOBS)),
):
    current_user, db = auth_data
    """
    Retrieve a job posting by ID.

    Requires VIEW_JOBS permission.

    Args:
        job_id (int): Job ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        JobResponse: Job object.

    Raises:
        HTTPException: If job not found.
    """
    job = job_repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# -------------------------
# List All Jobs
# -------------------------
@router.get("/", response_model=PaginatedResponse[JobResponse])
def list_jobs(
    pagination: PaginationParams = Depends(),
    search: str = None,
    location: str = None,
    job_type: str = None,
    experience_level: str = None,
    salary_min: float = None,
    salary_max: float = None,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_JOBS)),
):
    current_user, db = auth_data
    """
    List paginated and filtered job postings.

    Supports offset-based pagination and comprehensive filtering.

    Query Parameters:
        offset: Number of items to skip (default: 0)
        limit: Maximum items per page (default: 20, max: 100)
        search: Search in title, description, requirements
        location: Filter by job location
        job_type: Filter by job type (full-time, part-time, contract)
        experience_level: Filter by experience level (entry, mid, senior)
        salary_min: Minimum salary filter
        salary_max: Maximum salary filter

    Requires VIEW_JOBS permission.

    Args:
        pagination: Pagination parameters.
        search: Search term for job details.
        location: Job location filter.
        job_type: Job type filter.
        experience_level: Experience level filter.
        salary_min: Minimum salary filter.
        salary_max: Maximum salary filter.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        PaginatedResponse[JobResponse]: Paginated and filtered list of jobs.
    """
    # Create filter parameters
    filters = JobFilterParams(
        search=search,
        location=location,
        job_type=job_type,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max
    )
    
    # Get base query (candidates see all jobs, recruiters see company jobs)
    if current_user.role == "candidate":
        # Candidates can see all jobs
        query = job_repo.get_all_jobs_query(db)
    else:
        # Recruiters see only their company's jobs
        company = company_repo.get_company_by_user(db, current_user.user_id)
        if not company:
            raise HTTPException(
                status_code=400,
                detail="No company assigned to this user"
            )
        filters.company_id = company.company_id
        query = job_repo.get_company_jobs_query(db, company.company_id)
    
    # Apply filters
    query = apply_job_filters(query, filters)
    
    # Apply pagination
    jobs, total = paginate_query(query, pagination.offset, pagination.limit)
    
    return create_paginated_response(
        items=jobs,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
        page_class=JobResponse
    )


# -------------------------
# Update Job
# -------------------------
@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.EDIT_JOBS)),
):
    current_user, db = auth_data
    """
    Update an existing job posting.

    Requires EDIT_JOBS permission.

    Only job owner or admin can update.

    Args:
        job_id (int): Job ID.
        job_data (JobUpdate): Updated job data.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        JobResponse: Updated job.

    Raises:
        HTTPException: If job not found or unauthorized.
    """
    job = job_repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        return job_repo.update_job(db, job_id, job_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Delete Job
# -------------------------
@router.delete("/{job_id}", response_model=JobResponse)
def delete_job(
    job_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.DELETE_JOBS)),
):
    current_user, db = auth_data
    """
    Delete a job posting.

    Requires DELETE_JOBS permission.

    Args:
        job_id (int): Job ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        JobResponse: Deleted job.

    Raises:
        HTTPException: If job not found.
    """
    try:
        job = job_repo.delete_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

