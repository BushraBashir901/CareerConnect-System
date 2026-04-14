from fastapi import Depends, HTTPException, status
from typing import List, Callable, Optional
from app.core.auth import get_current_user
from app.core.rbac import (
    RoleEnum,
    PermissionEnum,
    has_permission,
    has_any_permission,
    has_all_permissions,
)
from app.models.user import User


def require_role(required_role: RoleEnum) -> Callable:
    """
    Dependency that restricts access to a specific role.

    Args:
        required_role (RoleEnum): Role required to access the endpoint.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if RoleEnum(current_user.role) != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker


def require_any_role(required_roles: List[RoleEnum]) -> Callable:
    """
    Dependency that allows access if user has any one of the required roles.

    Args:
        required_roles (List[RoleEnum]): List of allowed roles.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if RoleEnum(current_user.role) not in required_roles:
            roles_str = ", ".join([r.value for r in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {roles_str}"
            )
        return current_user
    return role_checker


def require_permission(required_permission: PermissionEnum) -> Callable:
    """
    Dependency that restricts access to a specific permission.

    Args:
        required_permission (PermissionEnum): Required permission.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(RoleEnum(current_user.role), required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission.value}"
            )
        return current_user
    return permission_checker


def require_any_permission(required_permissions: List[PermissionEnum]) -> Callable:
    """
    Dependency that allows access if user has any required permission.

    Args:
        required_permissions (List[PermissionEnum]): List of permissions.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_any_permission(RoleEnum(current_user.role), required_permissions):
            perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required any of: {perms_str}"
            )
        return current_user
    return permission_checker


def require_all_permissions(required_permissions: List[PermissionEnum]) -> Callable:
    """
    Dependency that requires all specified permissions.

    Args:
        required_permissions (List[PermissionEnum]): List of required permissions.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_all_permissions(RoleEnum(current_user.role), required_permissions):
            perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required all of: {perms_str}"
            )
        return current_user
    return permission_checker


def check_permissions(required_permissions: List[PermissionEnum], mode: str = "any") -> Callable:
    """
    Flexible permission checker supporting 'any' or 'all' mode.

    Args:
        required_permissions (List[PermissionEnum]): List of permissions to check.
        mode (str): 'any' or 'all' permission mode.

    Returns:
        Callable: FastAPI dependency function.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        role = RoleEnum(current_user.role)

        if mode == "any" and not has_any_permission(role, required_permissions):
            perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required any of: {perms_str}"
            )

        elif mode == "all" and not has_all_permissions(role, required_permissions):
            perms_str = ", ".join([p.value for p in required_permissions])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required all of: {perms_str}"
            )

        elif mode not in ("any", "all"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mode. Use 'any' or 'all'."
            )

        return current_user
    return permission_checker