from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean, Float
from app.core.database import Base

class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    selfie_asset_id = Column(Integer, ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    confidence_score = Column(Float, nullable=True)
    reviewed_by = Column(Integer, nullable=True)  # admin id
    rejection_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
