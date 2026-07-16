from sqlalchemy.orm import Session
from .engine import get_recommendations

def discover_profiles(db: Session, user_id: int, limit: int = 20, max_distance: int | None = None, min_age: int | None = None, max_age: int | None = None):
    age_override = (min_age, max_age) if min_age or max_age else None
    recs = get_recommendations(db, user_id, limit=limit, max_distance_override=max_distance, age_filters_override=age_override)
    return recs
