from enum import Enum
from typing import Set, List


class RoleEnum(str, Enum):
    """User roles in the system"""
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"


class PermissionEnum(str, Enum):
    """Permissions in the system"""
    # Team member management (for recruiters)
    MANAGE_TEAM_MEMBERS = "manage_team_members"
    VIEW_TEAM_MEMBERS = "view_team_members"
    
    # User management (for recruiters)
    MANAGE_USERS = "manage_users"
    
    # Company management
    MANAGE_COMPANIES = "manage_companies"
    VIEW_COMPANIES = "view_companies"
    
    # Job management
    CREATE_JOBS = "create_jobs"
    VIEW_JOBS = "view_jobs"
    EDIT_JOBS = "edit_jobs"
    DELETE_JOBS = "delete_jobs"
    
    # Applications
    CREATE_APPLICATIONS = "create_applications"
    VIEW_APPLICATIONS = "view_applications"
    MANAGE_APPLICATIONS = "manage_applications"
    
    # Interviews
    SCHEDULE_INTERVIEWS = "schedule_interviews"
    VIEW_INTERVIEWS = "view_interviews"
    MANAGE_INTERVIEWS = "manage_interviews"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    
    # AI Evaluation
    RUN_AI_EVALUATION = "run_ai_evaluation"


# Role-to-Permissions mapping
ROLE_PERMISSIONS: dict[RoleEnum, Set[PermissionEnum]] = {
    RoleEnum.RECRUITER: {
        # Recruiter has full control of their company and team
        PermissionEnum.MANAGE_COMPANIES,  # Can manage their own company
        PermissionEnum.VIEW_COMPANIES,    # Can view their company
        PermissionEnum.MANAGE_TEAM_MEMBERS,  # Can add/remove team members
        PermissionEnum.VIEW_TEAM_MEMBERS,     # Can view team members
        PermissionEnum.MANAGE_USERS,         # Can manage users
        PermissionEnum.CREATE_JOBS,
        PermissionEnum.VIEW_JOBS,
        PermissionEnum.EDIT_JOBS,
        PermissionEnum.DELETE_JOBS,
        PermissionEnum.VIEW_APPLICATIONS,
        PermissionEnum.MANAGE_APPLICATIONS,
        PermissionEnum.SCHEDULE_INTERVIEWS,
        PermissionEnum.VIEW_INTERVIEWS,
        PermissionEnum.MANAGE_INTERVIEWS,
        PermissionEnum.VIEW_REPORTS,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.RUN_AI_EVALUATION,
    },
    RoleEnum.CANDIDATE: {
        # Candidate has view-only permissions
        PermissionEnum.VIEW_COMPANIES,    # Can view companies (read-only)
        PermissionEnum.VIEW_JOBS,         # Can view jobs
        PermissionEnum.CREATE_APPLICATIONS,  # Can apply for jobs
        PermissionEnum.VIEW_APPLICATIONS,   # Can view own applications
        PermissionEnum.VIEW_INTERVIEWS,    # Can view own interviews
    },
}


# Helper functions
def has_permission(role: RoleEnum, permission: PermissionEnum) -> bool:
    role_permissions = ROLE_PERMISSIONS.get(role, [])
    return permission in role_permissions


def has_any_permission(role: RoleEnum, permissions: List[PermissionEnum]) -> bool:
    return any(has_permission(role, p) for p in permissions)


def has_all_permissions(role: RoleEnum, permissions: List[PermissionEnum]) -> bool:
    return all(has_permission(role, p) for p in permissions)
