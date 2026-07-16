from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class PreferenceUpdate(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_distance_km: Optional[int] = None
    show_me: Optional[str] = None  # male, female, everyone
    global_mode: Optional[bool] = None

class ProfileCreate(BaseModel):
    display_name: str
    bio: Optional[str] = ""
    birthdate: Optional[datetime] = None
    gender: Optional[str] = None
    interested_in: Optional[str] = "everyone"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    school: Optional[str] = None

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    birthdate: Optional[datetime] = None
    gender: Optional[str] = None
    interested_in: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    school: Optional[str] = None
    height_cm: Optional[int] = None
    show_me: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    bio: Optional[str]
    gender: Optional[str]
    interested_in: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    city: Optional[str]
    elo_score: float
    is_verified: bool
    show_me: bool
    age: Optional[int] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    school: Optional[str] = None
    created_at: datetime
    # Nested
    photos: List[dict] = []
    preferences: Optional[dict] = None

    class Config:
        from_attributes = True

    @field_validator("age", mode="before")
    @classmethod
    def compute_age(cls, v, info):
        # If age property method, handle
        return v

class DiscoverProfile(BaseModel):
    id: int
    user_id: int
    display_name: str
    bio: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    city: Optional[str]
    distance_km: Optional[float] = None
    job_title: Optional[str] = None
    school: Optional[str] = None
    elo_score: float
    photos: List[dict] = []
    is_verified: bool

    class Config:
        from_attributes = True
