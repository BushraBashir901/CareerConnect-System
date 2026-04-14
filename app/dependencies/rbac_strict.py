"""
Strict Role-Based Access Control (RBAC) Dependencies

Production-ready RBAC implementation with role-based access control.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.auth import get_current_user
from app.core.dependency import get_db
from app.core.rbac import RoleEnum, PermissionEnum
from app.models.user import User
from app.models.company import Company


def require_role(required_role: RoleEnum) -> callable:
    """
    Dependency that restricts access to a specific role.
    
    Args:
        required_role (RoleEnum): Required role to access endpoint
        
    Returns:
        callable: FastAPI dependency function
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if RoleEnum(current_user.role) != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker


def require_admin() -> callable:
    """Dependency that requires admin role."""
    return require_role(RoleEnum.ADMIN)


def require_recruiter() -> callable:
    """Dependency that requires recruiter role."""
    return require_role(RoleEnum.RECRUITER)


def require_candidate() -> callable:
    """Dependency that requires candidate role."""
    return require_role(RoleEnum.CANDIDATE)


def require_any_role(required_roles: list[RoleEnum]) -> callable:
    """
    Dependency that allows access if user has any of the required roles.
    
    Args:
        required_roles (list[RoleEnum]): List of allowed roles
        
    Returns:
        callable: FastAPI dependency function
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = RoleEnum(current_user.role)
        if user_role not in required_roles:
            roles_str = ", ".join([r.value for r in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required one of: {roles_str}"
            )
        return current_user
    return role_checker


def require_company_membership() -> callable:
    """
    Dependency that ensures user belongs to a company.
    Required for recruiters and admins accessing company-specific resources.
    
    Returns:
        callable: FastAPI dependency function
    """
    def company_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        user_role = RoleEnum(current_user.role)
        
        # Admins can access any company
        if user_role == RoleEnum.ADMIN:
            return current_user
            
        # Recruiters must have company_id
        if user_role == RoleEnum.RECRUITER:
            if not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters must belong to a company"
                )
            return current_user
            
        # Candidates cannot access company resources
        if user_role == RoleEnum.CANDIDATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidates cannot access company resources"
            )
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for company access"
        )
    
    return company_checker


def require_company_ownership() -> callable:
    """
    Dependency that ensures user owns the company resource.
    For recruiters accessing their own company data.
    
    Returns:
        callable: FastAPI dependency function
    """
    def ownership_checker(
        current_user: User = Depends(get_current_user), 
        db: Session = Depends(get_db),
        company_id: Optional[int] = None
    ) -> tuple[User, Session]:
        user_role = RoleEnum(current_user.role)
        
        # Admins can access any company
        if user_role == RoleEnum.ADMIN:
            return current_user, db
            
        # Recruiters can only access their own company
        if user_role == RoleEnum.RECRUITER:
            if not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters must belong to a company"
                )
            if company_id and current_user.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters can only access their own company"
                )
            return current_user, db
            
        # Candidates cannot access company resources
        if user_role == RoleEnum.CANDIDATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidates cannot access company resources"
            )
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for company access"
        )
    
    return ownership_checker


def require_self_access() -> callable:
    """
    Dependency that ensures users can only access their own resources.
    Used for profile management, applications, etc.
    
    Returns:
        callable: FastAPI dependency function
    """
    def self_access_checker(
        current_user: User = Depends(get_current_user),
        user_id: Optional[int] = None
    ) -> User:
        # Users can only access their own resources
        if user_id and current_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only access your own resources"
            )
        return current_user
    
    return self_access_checker


def require_permission_with_company_scope(required_permission: PermissionEnum) -> callable:
    """
    Dependency that checks permission and company scope.
    For job, application, and interview management.
    
    Args:
        required_permission (PermissionEnum): Required permission
        
    Returns:
        callable: FastAPI dependency function
    """
    def permission_checker(
        current_user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ) -> tuple[User, Session]:
        user_role = RoleEnum(current_user.role)
        
        # Check if user has the required permission
        from app.core.rbac import has_permission
        if not has_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission.value}"
            )
        
        # For company-scoped permissions, ensure user has company
        company_scoped_permissions = [
            PermissionEnum.CREATE_JOBS,
            PermissionEnum.EDIT_JOBS,
            PermissionEnum.DELETE_JOBS,
            PermissionEnum.MANAGE_APPLICATIONS,
            PermissionEnum.SCHEDULE_INTERVIEWS,
            PermissionEnum.MANAGE_INTERVIEWS,
            PermissionEnum.MANAGE_TEAM_MEMBERS,
            PermissionEnum.VIEW_TEAM_MEMBERS,
        ]
        
        if required_permission in company_scoped_permissions:
            if user_role == RoleEnum.RECRUITER and not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters must belong to a company to perform this action"
                )
        
        return current_user, db
    
    return permission_checker


def _with_company_scope(required_permission: PermissionEnum) -> callable:
    """
    Dependency that checks permission and company scope.
    For job, application, and interview management.
    
    Args:
        required_permission (PermissionEnum): Required permission
        
    Returns:
        callable: FastAPI dependency function
    """
    def permission_checker(
        current_user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ) -> tuple[User, Session]:
        user_role = RoleEnum(current_user.role)
        
        # Check if user has the required permission
        from app.core.rbac import has_permission
        if not has_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission.value}"
            )
        
        # For company-scoped permissions, ensure user has company
        company_scoped_permissions = [
            PermissionEnum.CREATE_JOBS,
            PermissionEnum.EDIT_JOBS,
            PermissionEnum.DELETE_JOBS,
            PermissionEnum.MANAGE_APPLICATIONS,
            PermissionEnum.SCHEDULE_INTERVIEWS,
            PermissionEnum.MANAGE_INTERVIEWS,
        ]
        
        if required_permission in company_scoped_permissions:
            if user_role == RoleEnum.RECRUITER and not current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters must belong to a company to perform this action"
                )
        
        return current_user, db
    
    return permission_checker


# Convenience functions for common role combinations
def require_admin_or_company_owner() -> callable:
    """Admin or company owner access."""
    return require_any_role([RoleEnum.ADMIN, RoleEnum.RECRUITER])


def require_recruiter_or_candidate() -> callable:
    """Recruiter or candidate access."""
    return require_any_role([RoleEnum.RECRUITER, RoleEnum.CANDIDATE])


def require_authenticated_user() -> callable:
    """Any authenticated user."""
    def auth_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        return current_user
    return auth_checker
