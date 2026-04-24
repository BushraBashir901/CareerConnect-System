from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.dependencies.rbac_strict import require_permission_with_company_scope, require_company_ownership, require_admin_or_company_owner
from app.core.rbac import PermissionEnum
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.repositories import company_repo

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse)
def create_company(
    company: CompanyCreate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_COMPANIES)),
    db: Session = Depends(get_db)
):
    """
    Create a new company.

    Requires MANAGE_COMPANIES permission.

    Args:
        company (CompanyCreate): Company input data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        CompanyResponse: Created company object.
    """
    # Admins can create any company, recruiters must be assigned to it
    created_company = company_repo.create_company(company, db, current_user)
    
    # For recruiters, automatically assign them to the created company
    if current_user.role == "recruiter":
        current_user.company_id = created_company.company_id
        db.commit()
        db.refresh(current_user)
    
    return created_company

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_COMPANIES)),
    db: Session = Depends(get_db)
):
    """
    Retrieve a company by ID.

    Requires MANAGE_COMPANIES permission.

    Args:
        company_id (int): Company ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        CompanyResponse: Company object.

    Raises:
        HTTPException: If company not found.
    """
    company = company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_COMPANIES)),
    db: Session = Depends(get_db)
):
    """
    Update an existing company.

    Requires MANAGE_COMPANIES permission.

    Args:
        company_id (int): Company ID.
        company_data (CompanyUpdate): Updated company data.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        CompanyResponse: Updated company object.

    Raises:
        HTTPException: If company not found.
    """
    company = company_repo.update_company(db, company_id, company_data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", response_model=CompanyResponse)
def delete_company(
    company_id: int,
    current_user=Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_COMPANIES)),
    db: Session = Depends(get_db)
):
    """
    Delete a company.

    Requires MANAGE_COMPANIES permission.

    Args:
        company_id (int): Company ID.
        current_user: Authenticated user with permission.
        db (Session): Database session.

    Returns:
        CompanyResponse: Deleted company object.

    Raises:
        HTTPException: If company not found.
    """
    company = company_repo.delete_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company