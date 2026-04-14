from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.repositories import report_repo
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportResponse)
def create_report(
    report: ReportCreate,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.GENERATE_REPORTS)),
):
    current_user, db = auth_data
    """
    Create a new report.

    Requires GENERATE_REPORTS permission.

    Args:
        report (ReportCreate): Report input data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        ReportResponse: Created report.
    """
    try:
        return report_repo.create_report(db, report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.VIEW_REPORTS)),
):
    current_user, db = auth_data
    """
    Retrieve a report by ID.

    Requires VIEW_REPORTS permission.
    Users can only view their own reports.

    Args:
        report_id (int): Report ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        ReportResponse: Report object.

    Raises:
        HTTPException: If report not found or unauthorized.
    """
    report = report_repo.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # User can only view their own reports
    if report.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only view your own reports")
    
    return report


@router.delete("/{report_id}", response_model=ReportResponse)
def delete_report(
    report_id: int,
    auth_data: tuple = Depends(require_permission_with_company_scope(PermissionEnum.GENERATE_REPORTS)),
):
    current_user, db = auth_data
    """
    Delete a report by ID.

    Requires GENERATE_REPORTS permission.
    Users can only delete their own reports.

    Args:
        report_id (int): Report ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        ReportResponse: Deleted report.

    Raises:
        HTTPException: If report not found or unauthorized.
    """
    # First get the report to check ownership
    report = report_repo.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # User can only delete their own reports
    if report.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own reports")
    
    # Now delete the report
    try:
        deleted_report = report_repo.delete_report(db, report_id)
        return deleted_report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))