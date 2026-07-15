from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import discover_profiles

router = APIRouter(prefix="/discovery", tags=["discovery"])

@router.get("/feed")
def get_feed(
    limit: int = Query(20, ge=1, le=100),
    max_distance_km: int | None = Query(None, ge=1, le=500),
    min_age: int | None = Query(None, ge=18, le=100),
    max_age: int | None = Query(None, ge=18, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return discover_profiles(db, current_user.id, limit=limit, max_distance=max_distance_km, min_age=min_age, max_age=max_age)

@router.get("/boost")
def boost_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Boost for 30 mins: sets is_boosted = True
    from datetime import datetime, timedelta, timezone
    from app.modules.users.repository import get_profile_by_user_id
    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(404, "Profile not found")
    profile.is_boosted = True
    profile.boosted_until = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.commit()
    # invalidate caches for others? Not needed, boost affects scoring
    return {"status": "boosted", "until": profile.boosted_until}
