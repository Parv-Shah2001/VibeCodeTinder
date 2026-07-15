from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Float, Boolean, JSON
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    stripe_payment_intent_id = Column(String(200), unique=True, nullable=True)
    stripe_customer_id = Column(String(200), nullable=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default="usd")
    status = Column(String(20), default="pending")  # pending, succeeded, failed, refunded
    tier = Column(String(20))  # plus, gold, platinum, boost, superlike
    product_type = Column(String(30))  # subscription, boost, superlike_pack
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    payment_id = Column(Integer, ForeignKey("payments.id"))
    amount_cents = Column(Integer)
    invoice_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
