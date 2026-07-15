"""
Explore + Top Picks + Likes You – Tinder Gold/Platinum features.
For 1M DAU, these are precomputed daily.

- Explore: grouped by interests (Music, Gaming, etc.)
- Top Picks: ML curated high Elo + profile completeness + activity
- Likes You: who's liked current user (Gold feature)
"""
from sqlalchemy.orm import Session
from app.modules.users.models import Profile
from app.modules.swipes.models import Swipe
from app.modules.media.models import MediaAsset
from typing import List
import random

INTERESTS = ["Music", "Gaming", "Travel", "Foodies", "Fitness", "Art", "Movies", "Sports", "Tech", "Pets"]

def get_explore_feed(db: Session, user_id: int, interest: str | None = None) -> dict:
    # Mock: filter by bio containing interest keyword, else random
    query = db.query(Profile).filter(Profile.user_id != user_id, Profile.show_me == True).limit(50).all()
    # Group by interests mock logic
    groups = {}
    for i in INTERESTS:
        # filter profiles whose bio contains letter? mock
        candidates = [p for p in query if random.random() > 0.5][:9]
        groups[i] = [
            {
                "user_id": p.user_id,
                "display_name": p.display_name,
                "photo": db.query(MediaAsset).filter(MediaAsset.user_id == p.user_id).first().public_url if db.query(MediaAsset).filter(MediaAsset.user_id == p.user_id).first() else None,
                "age": p.age(),
            }
            for p in candidates
        ]
    if interest:
        return {interest: groups.get(interest, [])}
    return groups

def get_top_picks(db: Session, user_id: int, limit: int = 10) -> List[dict]:
    # Top Picks: high Elo + verified + recent + profile completeness
    picks = db.query(Profile).filter(Profile.user_id != user_id, Profile.show_me == True).order_by(Profile.elo_score.desc()).limit(limit*2).all()
    # Sort by completeness + verified + Elo
    scored = []
    for p in picks:
        score = p.elo_score
        if p.is_verified:
            score += 50
        if p.bio:
            score += 20
        scored.append((p, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:limit]
    result = []
    for p, score in top:
        media = db.query(MediaAsset).filter(MediaAsset.user_id == p.user_id).order_by(MediaAsset.display_order).all()
        result.append({
            "user_id": p.user_id,
            "display_name": p.display_name,
            "age": p.age(),
            "bio": p.bio,
            "city": p.city,
            "photos": [{"url": m.public_url} for m in media],
            "score": score,
            "is_verified": p.is_verified,
        })
    return result

def get_likes_you(db: Session, user_id: int, limit: int = 50) -> List[dict]:
    # Who liked me – Gold feature
    likes = db.query(Swipe).filter(Swipe.swiped_id == user_id, Swipe.swipe_type.in_(["like", "superlike"])).order_by(Swipe.created_at.desc()).limit(limit).all()
    result = []
    for like in likes:
        profile = db.query(Profile).filter(Profile.user_id == like.swiper_id).first()
        if not profile:
            continue
        media = db.query(MediaAsset).filter(MediaAsset.user_id == profile.user_id).first()
        result.append({
            "swiper_id": like.swiper_id,
            "swipe_type": like.swipe_type,
            "created_at": like.created_at,
            "profile": {
                "display_name": profile.display_name,
                "age": profile.age(),
                "photo": media.public_url if media else None,
            }
        })
    return result
