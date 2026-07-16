from sqlalchemy.orm import Session
from .repository import get_profile_by_user_id, create_profile, update_profile, get_or_create_profile, update_preferences
from .models import Profile
from app.modules.media.repository import get_media_by_user_id
from app.core.events import event_bus, Events
import math

def handle_user_registered(event: dict):
    # Auto-create profile when user registers
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        user_id = event["user_id"]
        name = event.get("name") or f"User{user_id}"
        if not get_profile_by_user_id(db, user_id):
            create_profile(db, user_id, {"display_name": name})
            event_bus.publish(Events.PROFILE_CREATED, {"user_id": user_id})
    finally:
        db.close()

# Subscribe at import time
event_bus.subscribe(Events.USER_REGISTERED, handle_user_registered)

def create_or_update_profile_service(db: Session, user_id: int, data: dict) -> Profile:
    existing = get_profile_by_user_id(db, user_id)
    if existing:
        updated = update_profile(db, existing, data)
        event_bus.publish(Events.PROFILE_UPDATED, {"user_id": user_id, "profile_id": updated.id})
        return updated
    else:
        profile = create_profile(db, user_id, data)
        event_bus.publish(Events.PROFILE_CREATED, {"user_id": user_id, "profile_id": profile.id})
        return profile

def get_full_profile(db: Session, user_id: int) -> dict:
    profile = get_or_create_profile(db, user_id)
    media = get_media_by_user_id(db, user_id)
    photos = [{"id": m.id, "url": m.public_url, "is_primary": m.is_primary, "order": m.display_order} for m in media]
    # sort
    photos = sorted(photos, key=lambda x: x["order"])
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "display_name": profile.display_name,
        "bio": profile.bio,
        "gender": profile.gender,
        "interested_in": profile.interested_in,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "city": profile.city,
        "elo_score": profile.elo_score,
        "is_verified": profile.is_verified,
        "show_me": profile.show_me,
        "age": profile.age(),
        "job_title": profile.job_title,
        "company": profile.company,
        "school": profile.school,
        "created_at": profile.created_at,
        "photos": photos,
        "preferences": {
            "min_age": profile.preferences.min_age if profile.preferences else 18,
            "max_age": profile.preferences.max_age if profile.preferences else 60,
            "max_distance_km": profile.preferences.max_distance_km if profile.preferences else 50,
            "show_me": profile.preferences.show_me if profile.preferences else "everyone",
            "global_mode": profile.preferences.global_mode if profile.preferences else False,
        } if profile.preferences else None,
    }

def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R*c, 1)
