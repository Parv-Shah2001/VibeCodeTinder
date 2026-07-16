from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MediaResponse(BaseModel):
    id: int
    user_id: int
    public_url: str
    thumbnail_url: Optional[str]
    media_type: str
    status: str
    is_primary: bool
    display_order: int
    width: Optional[int]
    height: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class MediaUploadResponse(BaseModel):
    id: int
    public_url: str
    thumbnail_url: Optional[str] = None
    status: str
