from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import get_all_flags, get_flag, set_flag

router = APIRouter(prefix="/features", tags=["features"])

@router.get("")
def list_flags(current_user: User = Depends(get_current_user)):
    return get_all_flags(current_user.id)

@router.get("/{name}")
def check_flag(name: str, current_user: User = Depends(get_current_user)):
    enabled = get_flag(name, current_user.id)
    return {"flag": name, "enabled": enabled, "user_id": current_user.id}

@router.post("/{name}")
def update_flag(name: str, enabled: bool, rollout: int = 100, current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(403, "Admin only")
    set_flag(name, enabled, rollout)
    return {"flag": name, "enabled": enabled, "rollout": rollout}
