from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DiscoverRequest(BaseModel):
    limit: int = 20
    offset: int = 0
    max_distance_km: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

class DiscoverResponse(BaseModel):
    user_id: int
    display_name: str
    bio: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    city: Optional[str]
    distance_km: Optional[float]
    job_title: Optional[str]
    school: Optional[str]
    elo_score: float
    photos: List[dict]
    is_boosted: bool
    is_verified: bool
