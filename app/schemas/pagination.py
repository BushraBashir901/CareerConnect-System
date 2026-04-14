from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Standard pagination parameters for API endpoints.
    """
    offset: int = 0
    limit: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "offset": 0,
                "limit": 20
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format.
    """
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }
