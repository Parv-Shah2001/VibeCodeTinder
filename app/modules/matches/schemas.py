from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MatchResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    other_user: Optional[dict] = None
    created_at: datetime
    is_active: bool
    last_message_at: Optional[datetime] = None
    last_message: Optional[dict] = None

    class Config:
        from_attributes = True
