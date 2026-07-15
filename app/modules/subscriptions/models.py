from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean
from app.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    tier = Column(String(20), default="free")  # free, plus, gold, platinum
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    auto_renew = Column(Boolean, default=False)

    def has_feature(self, feature: str) -> bool:
        tier_order = {"free": 0, "plus": 1, "gold": 2, "platinum": 3}
        requirements = {
            "unlimited_likes": "plus",
            "see_who_liked": "gold",
            "superlike": "plus",
            "boost": "plus",
            "rewind": "plus",
            "passport": "plus",
            "top_picks": "gold",
            "priority_likes": "platinum",
        }
        req_tier = requirements.get(feature, "free")
        return tier_order.get(self.tier, 0) >= tier_order.get(req_tier, 0)
