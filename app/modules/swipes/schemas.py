from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SwipeCreate(BaseModel):
    swiped_id: int
    swipe_type: str = "like"  # like, dislike, superlike

    class Config:
        json_schema_extra = {
            "example": {"swiped_id": 123, "swipe_type": "like"}
        }

class SwipeResponse(BaseModel):
    id: int
    swiper_id: int
    swiped_id: int
    swipe_type: str
    created_at: datetime
    is_match: bool = False
    match_id: Optional[int] = None

    class Config:
        from_attributes = True
