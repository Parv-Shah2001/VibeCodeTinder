from sqlalchemy.orm import Session
from .models import MediaAsset
from typing import List, Optional

def get_media_by_user_id(db: Session, user_id: int) -> List[MediaAsset]:
    return db.query(MediaAsset).filter(MediaAsset.user_id == user_id, MediaAsset.conversation_id == None).order_by(MediaAsset.display_order).all()

def get_media_by_id(db: Session, media_id: int) -> Optional[MediaAsset]:
    return db.query(MediaAsset).filter(MediaAsset.id == media_id).first()

def count_user_media(db: Session, user_id: int) -> int:
    return db.query(MediaAsset).filter(MediaAsset.user_id == user_id, MediaAsset.conversation_id == None).count()

def create_media(db: Session, **kwargs) -> MediaAsset:
    asset = MediaAsset(**kwargs)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def delete_media(db: Session, asset: MediaAsset):
    db.delete(asset)
    db.commit()

def update_media_order(db: Session, user_id: int, ordered_ids: List[int]):
    for idx, media_id in enumerate(ordered_ids):
        db.query(MediaAsset).filter(MediaAsset.id == media_id, MediaAsset.user_id == user_id).update({"display_order": idx})
    db.commit()

def set_primary_photo(db: Session, user_id: int, media_id: int):
    db.query(MediaAsset).filter(MediaAsset.user_id == user_id).update({"is_primary": False})
    db.query(MediaAsset).filter(MediaAsset.id == media_id, MediaAsset.user_id == user_id).update({"is_primary": True})
    db.commit()
