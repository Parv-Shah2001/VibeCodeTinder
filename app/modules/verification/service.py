"""
Photo verification – selfie vs profile photos face match.
In prod: AWS Rekognition CompareFaces or custom model.
Flow: user uploads selfie -> compare with existing photos -> confidence >0.9 auto approve, else manual review.
"""
from sqlalchemy.orm import Session
from .models import VerificationRequest
from app.modules.media.repository import get_media_by_id
import random
import structlog

logger = structlog.get_logger(__name__)

def submit_verification(db: Session, user_id: int, selfie_asset_id: int) -> VerificationRequest:
    # Mock face comparison
    asset = get_media_by_id(db, selfie_asset_id)
    if not asset or asset.user_id != user_id:
        raise ValueError("Invalid selfie asset")

    # Simulate Rekognition CompareFaces confidence 0.7-0.99
    confidence = random.uniform(0.75, 0.99)
    status = "approved" if confidence > 0.9 else "pending"

    req = VerificationRequest(
        user_id=user_id,
        selfie_asset_id=selfie_asset_id,
        status=status,
        confidence_score=confidence,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    if status == "approved":
        from app.modules.users.repository import get_profile_by_user_id
        profile = get_profile_by_user_id(db, user_id)
        if profile:
            profile.is_verified = True
            db.commit()
        logger.info("verification_auto_approved", user_id=user_id, confidence=confidence)

    return req

def review_verification(db: Session, request_id: int, approved: bool, admin_id: int, reason: str | None = None):
    req = db.query(VerificationRequest).filter(VerificationRequest.id == request_id).first()
    if not req:
        raise ValueError("Request not found")
    req.status = "approved" if approved else "rejected"
    req.reviewed_by = admin_id
    req.rejection_reason = reason
    if approved:
        from app.modules.users.repository import get_profile_by_user_id
        profile = get_profile_by_user_id(db, req.user_id)
        if profile:
            profile.is_verified = True
    db.commit()
    db.refresh(req)
    return req

def get_verification_status(db: Session, user_id: int):
    return db.query(VerificationRequest).filter(VerificationRequest.user_id == user_id).order_by(VerificationRequest.created_at.desc()).first()
