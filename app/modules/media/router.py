from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import upload_profile_photo, delete_user_media, reorder_media, set_primary, upload_message_media
from .repository import get_media_by_user_id
from .schemas import MediaResponse

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/me", response_model=List[MediaResponse])
def list_my_media(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_media_by_user_id(db, current_user.id)

@router.post("/me/upload", response_model=MediaResponse)
def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = upload_profile_photo(db, current_user.id, file)
    return asset

@router.delete("/me/{media_id}")
def delete_photo(media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_user_media(db, current_user.id, media_id)
    return {"status": "deleted"}

@router.post("/me/reorder")
def reorder(ordered_ids: List[int], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assets = reorder_media(db, current_user.id, ordered_ids)
    return assets

@router.post("/me/{media_id}/primary")
def make_primary(media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = set_primary(db, current_user.id, media_id)
    return asset

# Message media upload
@router.post("/messages/{conversation_id}/upload", response_model=MediaResponse)
def upload_message_media_route(conversation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = upload_message_media(db, current_user.id, conversation_id, file)
    return asset
