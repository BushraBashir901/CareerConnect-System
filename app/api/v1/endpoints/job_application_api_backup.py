from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db
from app.dependencies.rbac_strict import get_current_user, require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.models.user import User
from app.repositories import job_application_repo
from app.schemas.job_application import JobApplicationCreate, JobApplicationResponse
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.utils.pagination import paginate_query, create_paginated_response
from app.utils.filtering import JobApplicationFilterParams, apply_job_application_filters
from app.utils.date_utils import parse_date_from_string

router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"]
)


@router.post("/jobs/{job_id}/apply", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    job_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.CREATE_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    Apply for a job - Candidates only.
    
    Automatically creates application with authenticated user's ID.

    Args:
        job_id (int): Job ID to apply for.
        current_user (User): Authenticated candidate user.
        db (Session): Database session.

    Returns:
        JobApplicationResponse: Created application.

    Raises:
        HTTPException: If user is not a candidate or job not found.
    """
    # Ensure only candidates can apply
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply for jobs")
    
    # Create application with auto-assigned user_id
    application_data = JobApplicationCreate(
        job_id=job_id,
        user_id=current_user.user_id
    )
    
    try:
        return job_application_repo.create_job_application(db, application_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs/{job_id}", response_model=list[JobApplicationResponse])
def list_applications_by_job(
    job_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    List all applicants for a specific job.

    Requires MANAGE_APPLICATIONS permission.

    Args:
        job_id (int): Job ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        list[JobApplicationResponse]: List of applications.
    """
    try:
        return job_application_repo.list_applications_by_job(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}/{user_id}", response_model=JobApplicationResponse)
def get_job_application(
    job_id: int,
    user_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    Retrieve a specific job application by job_id and user_id.

    Requires VIEW_APPLICATIONS permission.

    Args:
        job_id (int): Job ID.
        user_id (int): User ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        JobApplicationResponse: Application object.

    Raises:
        HTTPException: If application not found.
    """
    obj = job_application_repo.get_job_application(db, job_id, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Job Application not found")
    return obj


@router.delete("/{job_id}/{user_id}", response_model=JobApplicationResponse)
def delete_job_application(
    job_id: int,
    user_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    Delete a job application.

    Requires MANAGE_APPLICATIONS permission.

    Args:
        job_id (int): Job ID.
        user_id (int): User ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        JobApplicationResponse: Deleted application.

    Raises:
        HTTPException: If application not found.
    """
    obj = job_application_repo.delete_job_application(db, job_id, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Job Application not found")
    return obj


    """
    List all applicants for a specific job.

    Requires MANAGE_APPLICATIONS permission.

    Args:
        job_id (int): Job ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        list[JobApplicationResponse]: List of applications.
    """
    try:
        return job_application_repo.list_applications_by_job(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applicant/{user_id}", response_model=list[JobApplicationResponse])
def list_applications_by_user(
    user_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    List all job applications for a specific user.

    Candidates can only view their own applications.
    Recruiters can view applications for their company's jobs.

    Args:
        user_id (int): User ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        list[JobApplicationResponse]: List of applications.

    Raises:
        HTTPException: If unauthorized access.
    """
    # Candidates can only view their own applications
    if current_user.role == "candidate" and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Candidates can only view their own applications")
    
    try:
        return job_application_repo.list_applications_by_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[JobApplicationResponse])
def list_job_applications(
    pagination: PaginationParams = Depends(),
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_APPLICATIONS)),
):
    current_user, db = auth_data
    """
    List all job applications with role-based filtering and pagination.

    Candidates: See only their own applications
    Recruiters: See applications for their company's jobs only

    Query Parameters:
        offset: Number of items to skip (default: 0)
        limit: Maximum items per page (default: 20, max: 100)
        status: Filter by application status (pending, accepted, rejected)
        date_from: Filter applications submitted after this date
        date_to: Filter applications submitted before this date

    Requires VIEW_APPLICATIONS permission.

    Args:
        pagination: Pagination parameters.
        status: Application status filter.
        date_from: Start date filter.
        date_to: End date filter.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        PaginatedResponse[JobApplicationResponse]: Paginated list of applications.
    """
    # Create filter parameters
    filters = JobApplicationFilterParams(
        status=status,
        date_from=parse_date_from_string(date_from) if date_from else None,
        date_to=parse_date_from_string(date_to) if date_to else None
    )
    
    # Get base query based on user role
    if current_user.role == "candidate":
        # Candidates see only their own applications
        filters.user_id = current_user.user_id
        query = job_application_repo.get_user_applications_query(db, current_user.user_id)
    else:
        # Recruiters see applications for their company's jobs
        from app.repositories import company_repo
        company = company_repo.get_company_by_user(db, current_user.user_id)
        if not company:
            raise HTTPException(
                status_code=400,
                detail="No company assigned to this user"
            )
        filters.company_id = company.company_id
        query = job_application_repo.get_company_applications_query(db, company.company_id)
    
    # Apply filters
    query = apply_job_application_filters(query, filters)
    
    # Apply pagination
    applications, total = paginate_query(query, pagination.offset, pagination.limit)
    
    return create_paginated_response(
        items=applications,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
        page_class=JobApplicationResponse
    )