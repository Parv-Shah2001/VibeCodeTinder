from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tier: str
    is_active: bool
    started_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class SubscribeRequest(BaseModel):
    tier: str  # plus, gold, platinum
    auto_renew: bool = False
