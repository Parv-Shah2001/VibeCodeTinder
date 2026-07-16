from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import sms_service
from pydantic import BaseModel

router = APIRouter(prefix="/sms", tags=["sms"])

class PhoneRequest(BaseModel):
    phone: str

class VerifyRequest(BaseModel):
    phone: str
    otp: str

@router.post("/send-otp")
def send_otp(payload: PhoneRequest, current_user: User = Depends(get_current_user)):
    if not payload.phone:
        raise HTTPException(400, "Phone required")
    otp = sms_service.send_otp(payload.phone)
    return {"status": "sent", "phone": payload.phone, "dev_otp": otp}  # dev_otp only in non-prod

@router.post("/verify-otp")
def verify_otp(payload: VerifyRequest, current_user: User = Depends(get_current_user)):
    if sms_service.verify_otp(payload.phone, payload.otp):
        return {"status": "verified"}
    raise HTTPException(400, "Invalid OTP")
