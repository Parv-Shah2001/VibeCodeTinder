from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import email_service

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/verify")
async def send_verify(current_user: User = Depends(get_current_user)):
    await email_service.send_verification(current_user.email, "mock-token-123")
    return {"status": "sent"}

@router.post("/test-match")
async def test_match_email(other_name: str = "Alex", current_user: User = Depends(get_current_user)):
    await email_service.send_match_email(current_user.email, other_name)
    return {"status": "sent"}
