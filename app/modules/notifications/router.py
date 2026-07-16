from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import send_push_notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/test")
def test_notif(current_user: User = Depends(get_current_user)):
    send_push_notification(current_user.id, "Test", "This is a test notification")
    return {"status": "sent"}
