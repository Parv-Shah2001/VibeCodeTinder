"""
Pagination utilities for scale - cursor based for messages, offset for others.
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from fastapi import Query

T = TypeVar("T")

class PaginationParams(BaseModel):
    limit: int = Query(20, ge=1, le=100, description="Items per page")
    offset: int = Query(0, ge=0, description="Offset for pagination")

class CursorPaginationParams(BaseModel):
    limit: int = Query(20, ge=1, le=100)
    cursor: Optional[str] = Query(None, description="Cursor for next page (message id or created_at)")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: Optional[int] = None
    has_more: bool = False
    next_cursor: Optional[str] = None
    limit: int
    offset: int = 0

def paginate_query(query, limit: int, offset: int):
    total = query.count()
    items = query.limit(limit).offset(offset).all()
    return {
        "items": items,
        "total": total,
        "has_more": (offset + limit) < total,
        "limit": limit,
        "offset": offset,
    }
