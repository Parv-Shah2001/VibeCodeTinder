from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import search_profiles

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def search(q: str = Query(..., min_length=2), limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return search_profiles(db, q, limit)
