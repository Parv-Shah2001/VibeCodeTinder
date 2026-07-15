from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Enum, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class MediaType(str, enum.Enum):
    image = "image"
    video = "video"

class MediaStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"
    moderating = "moderating"

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    storage_key = Column(String(500), nullable=False)  # S3 key or local path
    public_url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    media_type = Column(String(20), default=MediaType.image)
    status = Column(String(20), default=MediaStatus.ready)
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    # For message media
    conversation_id = Column(Integer, nullable=True)
    # moderation
    is_nsfw = Column(Boolean, default=False)
    moderation_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="media_assets")

    def __repr__(self):
        return f"<MediaAsset id={self.id} user={self.user_id}>"
