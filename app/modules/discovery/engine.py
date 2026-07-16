"""
Recommendation Engine for Tinder-scale.

Targets:
- 50M users total
- 1M DAU
- Need to serve ~ 1B profile impressions/day (if 1M DAU * 1000 swipes/day avg)

Architecture thoughts for scale:
1. Candidate Generation (retrieval):
   - Geo-sharding: S2 cells / PostGIS. We partition earth into grids.
   - Preferences filter: age, gender, distance
   - Exclude already swiped: Redis Set + Bloom filter (for memory efficiency at 1B swipes/day)
   - Active users boost: users active last 24h ranked higher
   - New users boost: 500k new/day, give them visibility boost (newbie boost)
2. Ranking (scoring):
   - Elo score: base desirability
   - Activity score: message response rate, time spent
   - Profile completeness: bio, #photos
   - Diversity: don't show same city repeatedly, etc.
   - ML model placeholder: would be a two-tower model (user & item embeddings), trained on swipe data
3. Business rules:
   - Boosted users: is_boosted flag
   - Superlike priority
   - Verification, paid tiers get boost
4. Caching: Redis cache feed for 5 mins

For this modular monolith, we implement a practical SQL-based version that would be replaced by separate retrieval service in production.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List
import random

from app.modules.users.models import Profile, UserPreference
from app.modules.swipes.models import Swipe
from app.modules.media.models import MediaAsset
from .geo import haversine, get_bounding_box
from app.core.config import settings
from app.core.redis import redis_client
import json

CACHE_TTL = settings.RECOMMENDATION_CACHE_TTL_SECONDS

def _get_candidate_cache_key(user_id: int) -> str:
    return f"rec:candidates:{user_id}"

def compute_score(viewer: Profile, candidate: Profile, distance_km: float | None) -> float:
    score = candidate.elo_score  # base 1000

    # Distance penalty: closer = higher
    if distance_km is not None:
        # exponential decay
        score += max(0, 100 - distance_km)  # close bonus
    # Age preference matching
    # Activity: recent users higher
    if candidate.updated_at and (datetime.utcnow() - candidate.updated_at.replace(tzinfo=None)) < timedelta(hours=24):
        score += 50
    # New user boost
    if candidate.created_at and (datetime.utcnow() - candidate.created_at.replace(tzinfo=None)) < timedelta(days=3):
        score += 100
    # Boosted
    if candidate.is_boosted:
        score += 200
    # Verified
    if candidate.is_verified:
        score += 30
    # Profile completeness (bio + job etc)
    completeness = 0
    if candidate.bio:
        completeness += 10
    if candidate.job_title:
        completeness += 5
    if candidate.school:
        completeness += 5
    score += completeness

    # Randomization for diversity / exploration (epsilon-greedy)
    score += random.uniform(-10, 10)

    return score

def get_recommendations(db: Session, viewer_user_id: int, limit: int = 20, max_distance_override: int | None = None, age_filters_override: tuple | None = None) -> List[dict]:
    # Try cache
    cache_key = _get_candidate_cache_key(viewer_user_id)
    try:
        cached = redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            # simple cache hit, but need to slice fresh
            return data[:limit]
    except Exception:
        pass

    # Get viewer profile
    viewer_profile = db.query(Profile).filter(Profile.user_id == viewer_user_id).first()
    if not viewer_profile:
        return []

    viewer_pref = viewer_profile.preferences
    if not viewer_pref:
        from app.modules.users.models import UserPreference
        viewer_pref = UserPreference(profile_id=viewer_profile.id)

    max_distance = max_distance_override or viewer_pref.max_distance_km or settings.RECOMMENDATION_GEO_RADIUS_KM_DEFAULT
    min_age = age_filters_override[0] if age_filters_override else viewer_pref.min_age
    max_age = age_filters_override[1] if age_filters_override else viewer_pref.max_age
    interested_in = viewer_pref.show_me or viewer_profile.interested_in or "everyone"
    global_mode = viewer_pref.global_mode

    # Already swiped ids
    swiped_ids = db.query(Swipe.swiped_id).filter(Swipe.swiper_id == viewer_user_id).all()
    swiped_ids = [r[0] for r in swiped_ids]
    swiped_ids.append(viewer_user_id)  # exclude self

    # Geo bounding box
    bbox = None
    if not global_mode and viewer_profile.latitude and viewer_profile.longitude:
        bbox = get_bounding_box(viewer_profile.latitude, viewer_profile.longitude, max_distance)

    # Age calc: birthdate range
    from datetime import date
    today = date.today()
    # min_age 18 => max birthdate = today - 18 years
    # max_age 60 => min birthdate = today - 60 years
    def years_ago(y):
        try:
            return datetime(today.year - y, today.month, today.day)
        except ValueError:
            return datetime(today.year - y, 3, 1)

    max_birthdate = years_ago(min_age) if min_age else None
    min_birthdate = years_ago(max_age) if max_age else None

    query = db.query(Profile).filter(
        Profile.user_id.notin_(swiped_ids),
        Profile.show_me == True,
    )

    if interested_in != "everyone":
        query = query.filter(or_(Profile.gender == interested_in, Profile.gender == None))

    if max_birthdate:
        query = query.filter(or_(Profile.birthdate == None, Profile.birthdate <= max_birthdate))
    if min_birthdate:
        query = query.filter(or_(Profile.birthdate == None, Profile.birthdate >= min_birthdate))

    if bbox and not global_mode:
        query = query.filter(
            Profile.latitude >= bbox["min_lat"],
            Profile.latitude <= bbox["max_lat"],
            Profile.longitude >= bbox["min_lon"],
            Profile.longitude <= bbox["max_lon"],
        )

    # Limit candidate pool for scoring (e.g., 200)
    candidates = query.order_by(Profile.updated_at.desc()).limit(settings.RECOMMENDATION_CANDIDATE_LIMIT * 2).all()

    scored = []
    for cand in candidates:
        dist = None
        if viewer_profile.latitude and viewer_profile.longitude and cand.latitude and cand.longitude:
            dist = haversine(viewer_profile.latitude, viewer_profile.longitude, cand.latitude, cand.longitude)
            if not global_mode and dist is not None and dist > max_distance:
                continue
        score = compute_score(viewer_profile, cand, dist)
        scored.append((cand, dist, score))

    # Sort by score desc
    scored.sort(key=lambda x: x[2], reverse=True)

    # Take top
    top = scored[: settings.RECOMMENDATION_CANDIDATE_LIMIT]

    result = []
    for cand, dist, score in top:
        # Get media
        media = db.query(MediaAsset).filter(MediaAsset.user_id == cand.user_id, MediaAsset.conversation_id == None).order_by(MediaAsset.display_order).all()
        photos = [{"id": m.id, "url": m.public_url, "thumbnail_url": m.thumbnail_url, "is_primary": m.is_primary} for m in media]
        result.append({
            "user_id": cand.user_id,
            "profile_id": cand.id,
            "display_name": cand.display_name,
            "bio": cand.bio,
            "age": cand.age(),
            "gender": cand.gender,
            "city": cand.city,
            "distance_km": round(dist, 1) if dist else None,
            "job_title": cand.job_title,
            "school": cand.school,
            "elo_score": cand.elo_score,
            "photos": photos,
            "is_boosted": cand.is_boosted,
            "is_verified": cand.is_verified,
            "score": round(score, 2),
        })

    # Cache
    try:
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
    except Exception:
        pass

    return result[:limit]

def invalidate_cache(user_id: int):
    try:
        redis_client.delete(_get_candidate_cache_key(user_id))
    except Exception:
        pass
