from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import get_matches_with_profiles
from .repository import get_match_by_id, unmatch
from fastapi import HTTPException

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("")
def list_matches(limit: int = 100, offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_matches_with_profiles(db, current_user.id, limit, offset)

@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    match = get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    if current_user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(403, "Not your match")
    unmatch(db, match)
    return {"status": "unmatched"}

@router.get("/{match_id}")
def get_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    match = get_match_by_id(db, match_id)
    if not match or current_user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(404, "Match not found")
    from .service import get_matches_with_profiles
    # Simple
    return {
        "id": match.id,
        "user1_id": match.user1_id,
        "user2_id": match.user2_id,
        "created_at": match.created_at,
        "is_active": match.is_active,
    }
