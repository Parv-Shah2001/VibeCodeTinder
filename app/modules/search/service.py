"""
Search service – would use Elasticsearch / OpenSearch for 50M users.
Features: search by display_name, interests, city, job, school.
For MVP: SQL ILIKE + caching.
"""
from sqlalchemy.orm import Session
from app.modules.users.models import Profile
from app.modules.media.models import MediaAsset
from sqlalchemy import or_

def search_profiles(db: Session, query: str, limit: int = 20):
    if not query or len(query.strip()) < 2:
        return []
    q = f"%{query.lower()}%"
    results = db.query(Profile).filter(
        or_(
            Profile.display_name.ilike(q),
            Profile.bio.ilike(q),
            Profile.city.ilike(q),
            Profile.school.ilike(q),
            Profile.job_title.ilike(q),
        ),
        Profile.show_me == True
    ).limit(limit).all()

    enriched = []
    for p in results:
        media = db.query(MediaAsset).filter(MediaAsset.user_id == p.user_id).first()
        enriched.append({
            "user_id": p.user_id,
            "display_name": p.display_name,
            "bio": p.bio,
            "city": p.city,
            "age": p.age(),
            "photo": media.public_url if media else None,
        })
    return enriched
