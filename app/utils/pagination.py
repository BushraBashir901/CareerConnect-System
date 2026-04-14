from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from math import ceil

from app.schemas.pagination import PaginationParams, PaginatedResponse

T = TypeVar('T')


def paginate_query(query, offset: int, limit: int) -> tuple:
    """
    Apply pagination to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        offset: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (paginated_items, total_count)
    """
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return items, total


def create_paginated_response(
    items: List[T],
    total: int,
    offset: int,
    limit: int,
    page_class: type
) -> PaginatedResponse[T]:
    """
    Create a standardized paginated response.
    
    Args:
        items: List of items for current page
        total: Total number of items in database
        offset: Current offset
        limit: Current page limit
        page_class: Response model class
        
    Returns:
        PaginatedResponse with calculated pagination info
    """
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    return PaginatedResponse[
        page_class
    ](
        items=items,
        total=total,
        page=current_page,
        per_page=limit,
        pages=total_pages,
        has_next=current_page < total_pages,
        has_prev=current_page > 1
    )


def get_pagination_info(offset: int, limit: int, total: int) -> dict:
    """
    Get pagination metadata as dictionary.
    
    Args:
        offset: Current offset
        limit: Current limit
        total: Total items
        
    Returns:
        Dictionary with pagination info
    """
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    return {
        "total": total,
        "page": current_page,
        "per_page": limit,
        "pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1,
        "offset": offset,
        "limit": limit
    }
