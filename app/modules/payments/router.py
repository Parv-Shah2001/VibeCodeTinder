from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .schemas import CreatePaymentIntent
from .service import create_payment_intent, confirm_payment, handle_stripe_webhook

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create-intent")
def create_intent(payload: CreatePaymentIntent, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        payment = create_payment_intent(db, current_user.id, payload.tier, payload.product_type)
        return {
            "payment_id": payment.id,
            "client_secret": f"mock_secret_{payment.id}",  # In prod: real stripe client_secret
            "amount_cents": payment.amount_cents,
            "status": payment.status,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/confirm/{payment_id}")
def confirm(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = confirm_payment(db, payment_id)
    if payment.user_id != current_user.id:
        raise HTTPException(403, "Not yours")
    return payment

@router.get("/history")
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from .models import Payment
    return db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).limit(50).all()

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # In prod verify Stripe signature via stripe.Webhook.construct_event
    try:
        payload = await request.json()
        event_type = payload.get("type", "unknown")
        data = payload.get("data", {}).get("object", {})
        handle_stripe_webhook(db, event_type, data)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {str(e)}")
