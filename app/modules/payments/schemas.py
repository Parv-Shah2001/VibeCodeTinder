from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreatePaymentIntent(BaseModel):
    tier: str  # plus, gold, platinum
    product_type: str = "subscription"  # subscription, boost, superlike_pack
    # boost: 1 boost, superlike_pack: 5 superlikes

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount_cents: int
    currency: str
    status: str
    tier: Optional[str]
    product_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class StripeWebhookPayload(BaseModel):
    type: str
    data: dict
