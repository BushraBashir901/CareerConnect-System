from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.repositories import interview_repo
from app.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


# -------------------------
# Create
# -------------------------
@router.post("/", response_model=InterviewResponse)
def create_interview(
    data: InterviewCreate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_INTERVIEWS)),
    db: Session = Depends(get_db)
):
    """
    Create a new interview.

    Requires MANAGE_INTERVIEWS permission.

    Args:
        data (InterviewCreate): Interview input data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        InterviewResponse: Created interview object.

    Raises:
        HTTPException: If validation fails.
    """
    try:
        return interview_repo.create_interview(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Get
# -------------------------
@router.get("/{bot_id}/{user_id}", response_model=InterviewResponse)
def get_interview(
    bot_id: int,
    user_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.VIEW_INTERVIEWS)),
    db: Session = Depends(get_db)
):
    """
    Retrieve an interview by bot_id and user_id.

    Requires VIEW_INTERVIEWS permission.

    Args:
        bot_id (int): AI Bot ID.
        user_id (int): User ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        InterviewResponse: Interview object.

    Raises:
        HTTPException: If interview not found.
    """
    obj = interview_repo.get_interview(db, bot_id, user_id)

    if not obj:
        raise HTTPException(status_code=404, detail="AI Bot Applicant not found")

    return obj


# -------------------------
# Update
# -------------------------
@router.put("/{bot_id}/{user_id}", response_model=InterviewResponse)
def update_interview(
    bot_id: int,
    user_id: int,
    data: InterviewUpdate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_INTERVIEWS)),
    db: Session = Depends(get_db)
):
    """
    Update an existing interview.

    Requires MANAGE_INTERVIEWS permission.

    Args:
        bot_id (int): AI Bot ID.
        user_id (int): User ID.
        data (InterviewUpdate): Updated interview data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        InterviewResponse: Updated interview object.

    Raises:
        HTTPException: If interview not found or validation fails.
    """
    try:
        obj = interview_repo.update_interview(db, bot_id, user_id, data)

        if not obj:
            raise HTTPException(status_code=404, detail="AI Bot Applicant not found")

        return obj

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# Delete
# -------------------------
@router.delete("/{bot_id}/{user_id}", response_model=InterviewResponse)
def delete_interview(
    bot_id: int,
    user_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_INTERVIEWS)),
    db: Session = Depends(get_db)
):
    """
    Delete an interview.

    Requires MANAGE_INTERVIEWS permission.

    Args:
        bot_id (int): AI Bot ID.
        user_id (int): User ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        InterviewResponse: Deleted interview object.

    Raises:
        HTTPException: If interview not found.
    """
    obj = interview_repo.delete_interview(db, bot_id, user_id)

    if not obj:
        raise HTTPException(status_code=404, detail="AI Bot Application not found")

    return obj


# -------------------------
# List
# -------------------------
@router.get("/", response_model=list[InterviewResponse])
def list_interviews(
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.VIEW_INTERVIEWS)),
    db: Session = Depends(get_db)
):
    """
    List all interviews.

    Requires VIEW_INTERVIEWS permission.

    Args:
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        list[InterviewResponse]: List of interviews.
    """
    return interview_repo.list_interviews(db)