"""
Payment service – Stripe integration for subscriptions, boosts, superlike packs.

Scale: 1M DAU with ~5% paying = 50k paying users, ~1k transactions/min at peak
Need idempotent payment intents, webhook handling, reconciliation.

For 50M users scale, use Stripe webhooks + outbox pattern + idempotency keys.
"""
from sqlalchemy.orm import Session
from .models import Payment
from app.modules.subscriptions.service import subscribe
import structlog

logger = structlog.get_logger(__name__)

PRICING = {
    "plus": 999,        # $9.99
    "gold": 1499,       # $14.99
    "platinum": 1999,   # $19.99
    "boost": 699,       # $6.99 per boost
    "superlike_pack": 499,  # $4.99 for 5
}

def create_payment_intent(db: Session, user_id: int, tier: str, product_type: str = "subscription") -> Payment:
    if product_type == "subscription" and tier not in ("plus", "gold", "platinum"):
        raise ValueError("Invalid tier")
    amount = PRICING.get(tier if product_type == "subscription" else product_type, 999)

    # In production: stripe.PaymentIntent.create(amount=amount, currency="usd", customer=..., metadata={user_id, tier})
    payment = Payment(
        user_id=user_id,
        amount_cents=amount,
        currency="usd",
        status="pending",
        tier=tier if product_type == "subscription" else None,
        product_type=product_type,
        stripe_payment_intent_id=f"pi_mock_{user_id}_{amount}_{tier}",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    logger.info("payment_intent_created", payment_id=payment.id, user_id=user_id, amount=amount, tier=tier)
    return payment

def confirm_payment(db: Session, payment_id: int, stripe_intent_id: str | None = None):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise ValueError("Payment not found")
    payment.status = "succeeded"
    if stripe_intent_id:
        payment.stripe_payment_intent_id = stripe_intent_id
    db.commit()

    # Fulfill product
    if payment.product_type == "subscription" and payment.tier:
        subscribe(db, payment.user_id, payment.tier, auto_renew=True)
    elif payment.product_type == "boost":
        from app.modules.users.repository import get_profile_by_user_id
        from datetime import datetime, timedelta, timezone
        profile = get_profile_by_user_id(db, payment.user_id)
        if profile:
            profile.is_boosted = True
            profile.boosted_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            db.commit()
    elif payment.product_type == "superlike_pack":
        # Add superlikes to user – would have a superlike_balance table
        pass

    logger.info("payment_confirmed", payment_id=payment.id, user_id=payment.user_id)
    return payment

def handle_stripe_webhook(db: Session, event_type: str, data: dict):
    """
    Handle Stripe webhook events:
    - payment_intent.succeeded
    - invoice.payment_succeeded (subscription renewal)
    - customer.subscription.deleted
    """
    logger.info("stripe_webhook_received", event_type=event_type)
    if event_type == "payment_intent.succeeded":
        intent_id = data.get("id")
        # Find payment by intent_id
        payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == intent_id).first()
        if payment:
            payment.status = "succeeded"
            db.commit()
            # fulfill as above
    elif event_type == "invoice.payment_succeeded":
        # Handle subscription renewal
        pass
    return True
