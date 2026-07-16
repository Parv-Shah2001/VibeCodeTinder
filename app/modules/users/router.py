from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .schemas import ProfileCreate, ProfileUpdate, PreferenceUpdate
from .service import get_full_profile, create_or_update_profile_service
from .repository import get_profile_by_user_id, update_preferences, get_or_create_profile

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/profile")
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_full_profile(db, current_user.id)

@router.post("/me/profile")
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = create_or_update_profile_service(db, current_user.id, payload.model_dump(exclude_unset=True))
    return get_full_profile(db, current_user.id)

@router.patch("/me/profile")
def patch_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = get_or_create_profile(db, current_user.id)
    data = payload.model_dump(exclude_unset=True)
    from .repository import update_profile
    update_profile(db, profile, data)
    return get_full_profile(db, current_user.id)

@router.patch("/me/preferences")
def patch_preferences(payload: PreferenceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = get_or_create_profile(db, current_user.id)
    pref = update_preferences(db, profile, payload.model_dump(exclude_unset=True))
    return {"min_age": pref.min_age, "max_age": pref.max_age, "max_distance_km": pref.max_distance_km, "show_me": pref.show_me, "global_mode": pref.global_mode}

@router.get("/{user_id}/public")
def get_public_profile(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Basic public info, respecting privacy
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    if not profile.show_me and profile.user_id != current_user.id:
        raise HTTPException(403, "Profile hidden")
    from app.modules.media.repository import get_media_by_user_id
    media = get_media_by_user_id(db, user_id)
    photos = [{"id": m.id, "url": m.public_url, "is_primary": m.is_primary} for m in media]
    return {
        "user_id": profile.user_id,
        "display_name": profile.display_name,
        "bio": profile.bio,
        "age": profile.age(),
        "city": profile.city,
        "photos": photos,
        "is_verified": profile.is_verified,
    }
