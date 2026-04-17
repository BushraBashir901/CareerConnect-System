from fastapi import Depends, APIRouter, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.dependencies.rbac_strict import get_current_user, require_permission_with_company_scope
from app.core.rbac import PermissionEnum
from app.models.user import User
from app.models.user_resume import UserResume
from app.repositories import user_repo
from app.schemas.user import UserUpdate, UserResponse
from app.utils.file_validator import validate_file
from app.utils.parser import parse_data, extract_text
import os


router = APIRouter(prefix="/user", tags=["Users"])


# ========== USER MANAGEMENT ENDPOINTS ==========

# User creation moved to team endpoints - use POST /team/members instead


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a user by ID.

    Users can view their own profile.

    Args:
        user_id (int): User ID.
        current_user (User): Authenticated user.
        db (Session): Database session.

    Returns:
        UserResponse: User object.

    Raises:
        HTTPException: If unauthorized or user not found.
    """
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")

    user = user_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user profile.

    Users can update their own profile.

    Args:
        user_id (int): User ID.
        user_data (UserUpdate): Updated user data.
        current_user (User): Authenticated user.
        db (Session): Database session.

    Returns:
        UserResponse: Updated user object.

    Raises:
        HTTPException: If unauthorized or user not found.
    """
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # Prevent users from deactivating their own accounts
    if user_data.is_active == False and current_user.user_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    user = user_repo.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_permission_with_company_scope(PermissionEnum.MANAGE_TEAM_MEMBERS)),
    db: Session = Depends(get_db)
):
    """
    Deactivate a team member (requires MANAGE_TEAM_MEMBERS permission).

    Only recruiters can deactivate team members from their company.
    Cannot deactivate yourself.

    Args:
        user_id (int): User ID.
        current_user (User): Authenticated user with permission.
        db (Session): Database session.

    Returns:
        UserResponse: Deactivated user object.

    Raises:
        HTTPException: If unauthorized or user not found.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can deactivate team members")
    
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    user = user_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Cannot deactivate user from different company")
    
    user.is_active = False
    db.commit()
    return user


@router.post("/reactivate", response_model=UserResponse)
def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Temporary endpoint to reactivate user accounts for testing.
    
    Args:
        user_id (int): User ID to reactivate.
        db (Session): Database session.
    
    Returns:
        UserResponse: Reactivated user object.
    """
    user = user_repo.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/profile/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get profile of currently authenticated user.

    Args:
        current_user (User): Authenticated user.

    Returns:
        UserResponse: Current user profile.
    """
    return current_user

#-------------------------------------------------------#
# Resume Endpoints
#-------------------------------------------------------#

@router.post("/resume", response_model=dict)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a resume file.
    
    Args:
        file (UploadFile): Resume file to upload.
        current_user (User): Authenticated user.
    
    Returns:
        dict: Upload success message.
    """
    try:
        validate_file(file)
        
        os.makedirs("uploads",exist_ok=True)
        
        file_path=f"uploads/{file.filename}"
        
        with open(file_path,"wb") as f:
            f.write(file.file.read())
            text = extract_text(file_path)

        # 5. Parse data
        parsed_data = parse_data(text)

        # 6. Save to DB
        user_resume = UserResume(
            user_id=current_user.user_id,
            raw_text=text,
            clear_text=parsed_data
        )
        db.add(user_resume)
        db.commit()
        db.refresh(user_resume)

        return {
            "message": "Uploaded successfully",
            "file_path": file_path,
            "parsed_data": parsed_data,
            "resume_id": user_resume.user_resume_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/{user_id}")
async def get_resumes(user_id: str):
    return {"message": "Get resumes"}
    