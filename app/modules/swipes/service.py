from sqlalchemy.orm import Session
from fastapi import HTTPException
from .repository import has_swiped, create_swipe, get_swipe
from app.modules.matches.service import check_and_create_match
from app.core.redis import redis_client
from app.core.config import settings
from app.core.events import event_bus, Events
import time

SWIPE_SET_KEY = "swiped:{user_id}"

def _check_rate_limit(user_id: int):
    """
    Rate limit: settings.SWIPE_RATE_LIMIT_PER_MINUTE
    Uses Redis INCR with expiry; fallback to DB count.
    """
    key = f"ratelimit:swipes:{user_id}:{int(time.time()//60)}"
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, 60)
        if count > settings.SWIPE_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(429, "Swipe rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        # fallback: ignore if redis unavailable
        pass

def swipe_user(db: Session, swiper_id: int, swiped_id: int, swipe_type: str):
    if swiper_id == swiped_id:
        raise HTTPException(400, "Cannot swipe yourself")
    if swipe_type not in ("like", "dislike", "superlike"):
        raise HTTPException(400, "Invalid swipe type")

    _check_rate_limit(swiper_id)

    # Deduplication via Redis Set for speed (avoid DB hit for 1B swipes/day case)
    try:
        if redis_client.sismember(SWIPED_SET_KEY.format(user_id=swiper_id), swiped_id):
            raise HTTPException(400, "Already swiped this user")
    except HTTPException:
        raise
    except Exception:
        pass

    if has_swiped(db, swiper_id, swiped_id):
        raise HTTPException(400, "Already swiped this user")

    swipe = create_swipe(db, swiper_id, swiped_id, swipe_type)

    # Add to redis set for fast dedup
    try:
        redis_client.sadd(SWIPED_SET_KEY.format(user_id=swiper_id), swiped_id)
    except Exception:
        pass

    # Publish event for analytics, recommendation learning, etc.
    event_bus.publish(Events.SWIPE_CREATED, {
        "swiper_id": swiper_id,
        "swiped_id": swiped_id,
        "swipe_type": swipe_type,
        "swipe_id": swipe.id,
    })

    # Only need to check match if like/superlike
    match = None
    is_match = False
    if swipe_type in ("like", "superlike"):
        match = check_and_create_match(db, swiper_id, swiped_id)
        if match:
            is_match = True
            event_bus.publish(Events.MATCH_CREATED, {
                "match_id": match.id,
                "user1_id": match.user1_id,
                "user2_id": match.user2_id,
            })

    return {
        "id": swipe.id,
        "swiper_id": swipe.swiper_id,
        "swiped_id": swipe.swiped_id,
        "swipe_type": swipe.swipe_type,
        "created_at": swipe.created_at,
        "is_match": is_match,
        "match_id": match.id if match else None,
    }

def get_swipe_history(db: Session, user_id: int, limit: int = 50):
    from .models import Swipe
    return db.query(Swipe).filter(Swipe.swiper_id == user_id).order_by(Swipe.created_at.desc()).limit(limit).all()
