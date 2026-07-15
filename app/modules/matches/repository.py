from sqlalchemy.orm import Session
from .models import Match
from typing import List, Optional

def get_match_between(db: Session, user1: int, user2: int) -> Optional[Match]:
    # Ensure order for unique constraint (user1 < user2)
    u1, u2 = sorted([user1, user2])
    return db.query(Match).filter(Match.user1_id == u1, Match.user2_id == u2).first()

def create_match(db: Session, user1: int, user2: int) -> Match:
    u1, u2 = sorted([user1, user2])
    match = Match(user1_id=u1, user2_id=u2)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def list_matches_for_user(db: Session, user_id: int, limit: int = 100, offset: int = 0) -> List[Match]:
    return db.query(Match).filter(
        (Match.user1_id == user_id) | (Match.user2_id == user_id),
        Match.is_active == True
    ).order_by(Match.last_message_at.desc().nullslast(), Match.created_at.desc()).limit(limit).offset(offset).all()

def get_match_by_id(db: Session, match_id: int) -> Optional[Match]:
    return db.query(Match).filter(Match.id == match_id).first()

def unmatch(db: Session, match: Match):
    match.is_active = False
    db.commit()
