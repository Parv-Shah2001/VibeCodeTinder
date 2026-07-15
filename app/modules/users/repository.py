from sqlalchemy.orm import Session
from .models import Profile, UserPreference
from typing import Optional

def get_profile_by_user_id(db: Session, user_id: int) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.user_id == user_id).first()

def get_profile_by_id(db: Session, profile_id: int) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.id == profile_id).first()

def create_profile(db: Session, user_id: int, data: dict) -> Profile:
    profile = Profile(user_id=user_id, **data)
    db.add(profile)
    db.flush()
    # create default preferences
    pref = UserPreference(profile_id=profile.id)
    db.add(pref)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile(db: Session, profile: Profile, data: dict) -> Profile:
    for k, v in data.items():
        if v is not None and hasattr(profile, k):
            setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile

def get_or_create_profile(db: Session, user_id: int) -> Profile:
    p = get_profile_by_user_id(db, user_id)
    if p:
        return p
    return create_profile(db, user_id, {"display_name": f"User{user_id}"})

def update_preferences(db: Session, profile: Profile, data: dict) -> UserPreference:
    pref = profile.preferences
    if not pref:
        pref = UserPreference(profile_id=profile.id)
        db.add(pref)
        db.flush()
    for k, v in data.items():
        if v is not None and hasattr(pref, k):
            setattr(pref, k, v)
    db.commit()
    db.refresh(pref)
    return pref
