from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_match_users"),
        Index("ix_match_user1", "user1_id"),
        Index("ix_match_user2", "user2_id"),
        Index("ix_match_created", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # For scaling 1B matches/day, we consider time-based partitioning
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    def other_user_id(self, current_user_id: int) -> int:
        return self.user2_id if self.user1_id == current_user_id else self.user1_id

    def __repr__(self):
        return f"<Match {self.user1_id} <-> {self.user2_id}>"
