from sqlalchemy.orm import Session
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.core.dependency import get_db
from app.dependencies.rbac import get_current_user
from app.models.user import User
from fastapi import Depends


# def create_company(
#     company_data: CompanyCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)) -> Company:
#     """
#     Create a new company in the database.

#     Args:
#         db (Session): SQLAlchemy database session.
#         company_data (CompanyCreate): Company input data.

#     Returns:
#         Company: Created company object.
#     """
#     db_company = Company(
#         company_name=company_data.company_name,
#         description=company_data.description,
#         website=str(company_data.website) if company_data.website else None,
#         created_at=company_data.created_at
#     )
#     db.add(db_company)
#     db.commit()
#     db.refresh(db_company)
#     current_user.company_id = db_company.company_id  # Associate user with the new company
#     db.commit()  # Save the updated user record
#     return db_company

def create_company(company_data: CompanyCreate, db: Session, current_user: User):
    db_company = Company(
        company_name=company_data.company_name,
        description=company_data.description,
        website=str(company_data.website) if company_data.website else None,
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    # ✅ IMPORTANT FIX
    db_user = db.query(User).filter(User.user_id == current_user.user_id).first()

    db_user.company_id = db_company.company_id

    db.commit()
    db.refresh(db_user)

    return db_company  # ← ADD RETURN STATEMENT


def get_company(db: Session, company_id: int) -> Company | None:
    """
    Retrieve a company by its ID.

    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): Company ID.

    Returns:
        Company | None: Company object if found, otherwise None.
    """
    return db.query(Company).filter(Company.company_id == company_id).first()


def update_company(db: Session, company_id: int, company_data: CompanyUpdate) -> Company | None:
    """
    Update an existing company.

    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): ID of the company to update.
        company_data (CompanyUpdate): Updated company data.

    Returns:
        Company | None: Updated company object if found, otherwise None.
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return None

    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_company, field, value)

    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> Company | None:
    """
    Delete a company from the database.

    Args:
        db (Session): SQLAlchemy database session.
        company_id (int): Company ID.

    Returns:
        Company | None: Deleted company object if found, otherwise None.
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return None

    db.delete(db_company)
    db.commit()
    return db_company


def list_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    """
    Retrieve a list of companies with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of companies to return.

    Returns:
        list[Company]: List of company objects.
    """
    return db.query(Company).offset(skip).limit(limit).all()

# get company by user id - FIXED VERSION
def get_company_by_user(db: Session, user_id: int) -> Company | None:
    """
    Get company associated with a user.
    
    Args:
        db (Session): Database session
        user_id (int): User ID to find company for
        
    Returns:
        Company | None: Company if user has one, otherwise None
        
    Raises:
        ValueError: If user not found
    """
    # First verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    # Check if user has company_id
    if not user.company_id:
        return None  # User has no company (candidate or recruiter without company)
    
    # Get company using the user's company_id
    return db.query(Company).filter(Company.company_id == user.company_id).first()


def get_company_from_current_user(db: Session, current_user: User) -> Company | None:
    """
    Production-level function to get company from authenticated user.
    
    Args:
        db (Session): Database session
        current_user (User): Authenticated user object
        
    Returns:
        Company | None: Company if recruiter has one, None for candidates
        
    Raises:
        ValueError: If user not found in database
        HTTPException: If user is not a recruiter but tries to access company
    """
    # Refresh user from database to get latest data
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise ValueError(f"User with id {current_user.user_id} not found")
    
    # Handle different user roles
    if user.role == "candidate":
        return None  # Candidates don't have companies
    if user.role in ["recruiter", "admin"]:
        if not user.company_id:
            return None  # Recruiter/admin without company
        return db.query(Company).filter(Company.company_id == user.company_id).first()
    
    # Unknown role
    return None