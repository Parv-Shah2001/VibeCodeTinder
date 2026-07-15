from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class SwipeType(str, enum.Enum):
    like = "like"
    dislike = "dislike"  # pass
    superlike = "superlike"

class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        UniqueConstraint("swiper_id", "swiped_id", name="uq_swiper_swiped"),
        Index("ix_swiper_created", "swiper_id", "created_at"),
        Index("ix_swiped_created", "swiped_id", "created_at"),
        # For scaling: partitioning by created_at would be done in PG declarative partitioning
    )

    id = Column(Integer, primary_key=True, index=True)
    swiper_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    swiped_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    swipe_type = Column(String(20), nullable=False, default=SwipeType.like)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Swipe {self.swiper_id} -> {self.swiped_id} {self.swipe_type}>"
