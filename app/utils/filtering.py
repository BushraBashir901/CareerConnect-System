from typing import Optional, List, Any, Dict
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Query
from datetime import datetime, date
import re


class FilterParams:
    """
    Base class for filter parameters.
    """
    
    @classmethod
    def create_from_query_params(cls, **kwargs) -> Dict[str, Any]:
        """
        Create filter parameters from query parameters.
        
        Args:
            **kwargs: Query parameters from request
            
        Returns:
            Dictionary of filter parameters
        """
        filters = {}
        for key, value in kwargs.items():
            if value is not None and value != "":
                filters[key] = value
        return filters


class JobFilterParams:
    """
    Filter parameters for job listings.
    """
    
    def __init__(
        self,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        company_id: Optional[int] = None
    ):
        self.search = search
        self.location = location
        self.job_type = job_type
        self.experience_level = experience_level
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.company_id = company_id
    
    @classmethod
    def from_query_params(cls, **kwargs) -> 'JobFilterParams':
        """Create from query parameters."""
        return cls(
            search=kwargs.get('search'),
            location=kwargs.get('location'),
            job_type=kwargs.get('job_type'),
            experience_level=kwargs.get('experience_level'),
            salary_min=kwargs.get('salary_min'),
            salary_max=kwargs.get('salary_max'),
            company_id=kwargs.get('company_id')
        )


class TeamInvitationFilterParams:
    """
    Filter parameters for team invitations.
    """
    
    def __init__(
        self,
        status: Optional[str] = None,
        invited_email: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ):
        self.status = status
        self.invited_email = invited_email
        self.date_from = date_from
        self.date_to = date_to
    
    @classmethod
    def from_query_params(cls, **kwargs) -> 'TeamInvitationFilterParams':
        """Create from query parameters."""
        return cls(
            status=kwargs.get('status'),
            invited_email=kwargs.get('invited_email'),
            date_from=kwargs.get('date_from'),
            date_to=kwargs.get('date_to')
        )


class UserFilterParams:
    """
    Filter parameters for user management.
    """
    
    def __init__(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        company_id: Optional[int] = None
    ):
        self.role = role
        self.status = status
        self.search = search
        self.company_id = company_id
    
    @classmethod
    def from_query_params(cls, **kwargs) -> 'UserFilterParams':
        """Create from query parameters."""
        return cls(
            role=kwargs.get('role'),
            status=kwargs.get('status'),
            search=kwargs.get('search'),
            company_id=kwargs.get('company_id')
        )


class JobApplicationFilterParams:
    """
    Filter parameters for job applications.
    """
    
    def __init__(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.user_id = user_id
        self.company_id = company_id
    
    @classmethod
    def from_query_params(cls, **kwargs) -> 'JobApplicationFilterParams':
        """Create from query parameters."""
        return cls(
            date_from=kwargs.get('date_from'),
            date_to=kwargs.get('date_to'),
            user_id=kwargs.get('user_id'),
            company_id=kwargs.get('company_id')
        )


class ReportFilterParams:
    """
    Filter parameters for reports.
    """
    
    def __init__(
        self,
        report_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        user_id: Optional[int] = None
    ):
        self.report_type = report_type
        self.date_from = date_from
        self.date_to = date_to
        self.user_id = user_id
    
    @classmethod
    def from_query_params(cls, **kwargs) -> 'ReportFilterParams':
        """Create from query parameters."""
        return cls(
            report_type=kwargs.get('report_type'),
            date_from=kwargs.get('date_from'),
            date_to=kwargs.get('date_to'),
            user_id=kwargs.get('user_id')
        )


def apply_job_filters(query: Query, filters: JobFilterParams) -> Query:
    """
    Apply filters to job query.
    
    Args:
        query: SQLAlchemy query object
        filters: JobFilterParams object
        
    Returns:
        Filtered query
    """
    from app.models.job import Job
    
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Job.job_title.ilike(search_term),
                Job.job_description.ilike(search_term)
            )
        )
    
    if filters.location:
        query = query.filter(Job.location.ilike(f"%{filters.location}%"))
    
    if filters.job_type:
        query = query.filter(Job.job_type == filters.job_type)
    
    if filters.experience_level:
        query = query.filter(Job.experience_level == filters.experience_level)
    
    if filters.salary_min is not None:
        query = query.filter(Job.salary_range.ilike(f"${filters.salary_min:,.0f}%"))
    
    if filters.salary_max is not None:
        query = query.filter(Job.salary_range.ilike(f"%${filters.salary_max:,.0f}"))
    
    if filters.company_id:
        query = query.filter(Job.company_id == filters.company_id)
    
    return query


def apply_team_invitation_filters(query: Query, filters: TeamInvitationFilterParams) -> Query:
    """
    Apply filters to team invitation query.
    
    Args:
        query: SQLAlchemy query object
        filters: TeamInvitationFilterParams object
        
    Returns:
        Filtered query
    """
    from app.models.team_invitation import TeamInvitation
    
    if filters.status:
        query = query.filter(TeamInvitation.status == filters.status)
    
    if filters.invited_email:
        query = query.filter(TeamInvitation.invited_email.ilike(f"%{filters.invited_email}%"))
    
    if filters.date_from:
        query = query.filter(TeamInvitation.created_at >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(TeamInvitation.created_at <= filters.date_to)
    
    return query


def apply_user_filters(query: Query, filters: UserFilterParams) -> Query:
    """
    Apply filters to user query.
    
    Args:
        query: SQLAlchemy query object
        filters: UserFilterParams object
        
    Returns:
        Filtered query
    """
    from app.models.user import User
    
    if filters.role:
        query = query.filter(User.role == filters.role)
    
    if filters.status:
        query = query.filter(User.status == filters.status)
    
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    return query


def apply_job_application_filters(query: Query, filters: JobApplicationFilterParams) -> Query:
    """
    Apply filters to job application query.
    
    Args:
        query: SQLAlchemy query object
        filters: JobApplicationFilterParams object
        
    Returns:
        Filtered query
    """
    from app.models.job_application import Job_Application
    
    # Note: Job_Application model doesn't have status field
    # Status filtering would need to be implemented via joins with other tables
    
    if filters.date_from:
        query = query.filter(Job_Application.applied_at >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(Job_Application.applied_at <= filters.date_to)
    
    if filters.user_id:
        query = query.filter(Job_Application.user_id == filters.user_id)
    
    # Note: company_id filtering is handled at the query level before applying filters
    
    return query


def apply_report_filters(query: Query, filters: ReportFilterParams) -> Query:
    """
    Apply filters to report query.
    
    Args:
        query: SQLAlchemy query object
        filters: ReportFilterParams object
        
    Returns:
        Filtered query
    """
    from app.models.report import Report
    
    if filters.report_type:
        query = query.filter(Report.report_type == filters.report_type)
    
    if filters.date_from:
        query = query.filter(Report.created_at >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(Report.created_at <= filters.date_to)
    
    if filters.user_id:
        query = query.filter(Report.user_id == filters.user_id)
    
    return query


def parse_date_from_string(date_str: str) -> Optional[date]:
    """
    Parse date from string in various formats.
    
    Args:
        date_str: Date string
        
    Returns:
        Parsed date or None
    """
    if not date_str:
        return None
    
    # Try common date formats
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def validate_filter_params(filters: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
    """
    Validate and clean filter parameters.
    
    Args:
        filters: Raw filter parameters
        allowed_fields: List of allowed field names
        
    Returns:
        Validated filter parameters
    """
    validated = {}
    
    for key, value in filters.items():
        if key in allowed_fields and value is not None and value != "":
            validated[key] = value
    
    return validated
