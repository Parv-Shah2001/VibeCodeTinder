from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import io

from .repository import create_media, get_media_by_user_id, get_media_by_id, delete_media, count_user_media, set_primary_photo
from .processor import validate_file, process_image, mock_nsfw_check, mock_virus_scan
from app.core.s3 import get_storage
from app.core.config import settings
from app.core.events import event_bus, Events

storage = get_storage()

def upload_profile_photo(db: Session, user_id: int, file: UploadFile):
    # Rate check for scale: up to 9 photos per user
    count = count_user_media(db, user_id)
    if count >= settings.MAX_PHOTOS_PER_USER:
        raise HTTPException(400, f"Max {settings.MAX_PHOTOS_PER_USER} photos allowed")

    content = file.file.read()
    size = len(content)
    content_type = file.content_type or "image/jpeg"

    try:
        validate_file(content_type, size)
        if not mock_virus_scan(content):
            raise HTTPException(400, "File failed security scan")
        is_nsfw, score = mock_nsfw_check(content)
        if is_nsfw:
            raise HTTPException(400, "Image violates content policy")

        main_bytes, thumb_bytes, (w, h) = process_image(content)

    except ValueError as e:
        raise HTTPException(400, str(e))

    # Save main
    main_key, main_url = storage.save(io.BytesIO(main_bytes), folder="profile", content_type="image/jpeg")
    # Save thumb
    thumb_key, thumb_url = storage.save(io.BytesIO(thumb_bytes), folder="profile", content_type="image/jpeg")

    # If first photo, set primary
    is_primary = count == 0

    asset = create_media(
        db,
        user_id=user_id,
        storage_key=main_key,
        public_url=main_url,
        thumbnail_url=thumb_url,
        media_type="image",
        status="ready",
        is_primary=is_primary,
        display_order=count,
        width=w,
        height=h,
        size_bytes=size,
        moderation_score=score,
    )

    event_bus.publish(Events.MEDIA_UPLOADED, {"user_id": user_id, "media_id": asset.id, "url": main_url})

    return asset

def upload_message_media(db: Session, user_id: int, conversation_id: int, file: UploadFile):
    content = file.file.read()
    size = len(content)
    content_type = file.content_type or "image/jpeg"

    if size > settings.MAX_MEDIA_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"Max size {settings.MAX_MEDIA_SIZE_MB} MB")

    # For messages we allow images, videos, etc but simplified
    main_key, main_url = storage.save(io.BytesIO(content), folder="message", content_type=content_type)

    thumb_url = None
    if content_type.startswith("image/"):
        try:
            _, thumb_bytes, _ = process_image(content)
            _, thumb_url = storage.save(io.BytesIO(thumb_bytes), folder="message", content_type="image/jpeg")
        except:
            pass

    asset = create_media(
        db,
        user_id=user_id,
        storage_key=main_key,
        public_url=main_url,
        thumbnail_url=thumb_url,
        media_type="image" if content_type.startswith("image/") else "video",
        status="ready",
        conversation_id=conversation_id,
        size_bytes=size,
    )
    return asset

def delete_user_media(db: Session, user_id: int, media_id: int):
    asset = get_media_by_id(db, media_id)
    if not asset or asset.user_id != user_id:
        raise HTTPException(404, "Media not found")
    storage.delete(asset.storage_key, folder="profile")
    delete_media(db, asset)
    return True

def reorder_media(db: Session, user_id: int, ordered_ids: list[int]):
    from .repository import update_media_order
    update_media_order(db, user_id, ordered_ids)
    return get_media_by_user_id(db, user_id)

def set_primary(db: Session, user_id: int, media_id: int):
    asset = get_media_by_id(db, media_id)
    if not asset or asset.user_id != user_id:
        raise HTTPException(404, "Media not found")
    set_primary_photo(db, user_id, media_id)
    return asset
