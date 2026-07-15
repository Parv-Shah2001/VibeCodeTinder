from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import submit_verification, get_verification_status, review_verification
from pydantic import BaseModel

router = APIRouter(prefix="/verification", tags=["verification"])

class SubmitRequest(BaseModel):
    selfie_asset_id: int

@router.post("/submit")
def submit(payload: SubmitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        req = submit_verification(db, current_user.id, payload.selfie_asset_id)
        return req
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/status")
def status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = get_verification_status(db, current_user.id)
    return req or {"status": "not_submitted"}

@router.post("/review/{request_id}")
def review(request_id: int, approved: bool, reason: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(403, "Admin only")
    return review_verification(db, request_id, approved, current_user.id, reason)
