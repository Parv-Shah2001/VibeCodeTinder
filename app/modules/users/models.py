from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, func, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False, default="")
    bio = Column(Text, nullable=True, default="")
    birthdate = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, nonbinary, etc.
    interested_in = Column(String(50), nullable=True, default="everyone")  # male, female, everyone
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)
    school = Column(String(100), nullable=True)
    height_cm = Column(Integer, nullable=True)
    # For scaling: denormalized counters
    elo_score = Column(Float, default=1000.0, index=True)  # like Tinder's desirability
    swipe_count = Column(Integer, default=0)
    match_count = Column(Integer, default=0)
    is_boosted = Column(Boolean, default=False)
    boosted_until = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False)
    show_me = Column(Boolean, default=True)  # discoverable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
    preferences = relationship("UserPreference", back_populates="profile", uselist=False, cascade="all, delete-orphan")

    def age(self):
        if not self.birthdate:
            return None
        from datetime import date
        today = date.today()
        b = self.birthdate.date() if isinstance(self.birthdate, datetime) else self.birthdate
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, index=True)
    min_age = Column(Integer, default=18)
    max_age = Column(Integer, default=60)
    max_distance_km = Column(Integer, default=50)
    show_me = Column(String(20), default="everyone")
    global_mode = Column(Boolean, default=False)  # if True ignore distance
    # Advanced filters (Gold / Platinum features)
    has_bio = Column(Boolean, nullable=True)
    has_photos = Column(Boolean, nullable=True)

    profile = relationship("Profile", back_populates="preferences")
