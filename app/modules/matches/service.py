from sqlalchemy.orm import Session
from .repository import get_match_between, create_match
from app.modules.swipes.repository import get_swipe
from app.modules.messaging.repository import get_or_create_conversation

def check_and_create_match(db: Session, swiper_id: int, swiped_id: int):
    """
    Check if mutual like -> create match.
    Optimistic locking for high concurrency: 1B matches/day means high race.
    We use get_swipe + unique constraint handling.
    """
    # Check if swiped_id had already liked swiper_id
    existing_like = get_swipe(db, swiped_id, swiper_id)
    if not existing_like:
        return None
    if existing_like.swipe_type not in ("like", "superlike"):
        return None

    # mutual like -> check existing match
    existing_match = get_match_between(db, swiper_id, swiped_id)
    if existing_match:
        return existing_match

    try:
        match = create_match(db, swiper_id, swiped_id)
        # Auto-create conversation
        get_or_create_conversation(db, swiper_id, swiped_id)
        return match
    except Exception as e:
        # Race condition: another process created match, fetch it
        db.rollback()
        return get_match_between(db, swiper_id, swiped_id)

def get_matches_with_profiles(db: Session, user_id: int, limit: int = 100, offset: int = 0):
    from .repository import list_matches_for_user
    matches = list_matches_for_user(db, user_id, limit, offset)
    # Enrich with other user profile
    from app.modules.users.repository import get_profile_by_user_id
    from app.modules.media.repository import get_media_by_user_id
    from app.modules.messaging.repository import get_last_message_for_conversation, get_conversation_between

    result = []
    for m in matches:
        other_id = m.other_user_id(user_id)
        profile = get_profile_by_user_id(db, other_id)
        media = get_media_by_user_id(db, other_id)
        conv = get_conversation_between(db, user_id, other_id)
        last_msg = None
        if conv:
            lm = get_last_message_for_conversation(db, conv.id)
            if lm:
                last_msg = {"content": lm.content, "created_at": lm.created_at, "sender_id": lm.sender_id}

        result.append({
            "id": m.id,
            "user1_id": m.user1_id,
            "user2_id": m.user2_id,
            "other_user": {
                "user_id": other_id,
                "display_name": profile.display_name if profile else f"User{other_id}",
                "photo": media[0].public_url if media else None,
                "age": profile.age() if profile else None,
            },
            "created_at": m.created_at,
            "is_active": m.is_active,
            "last_message_at": m.last_message_at,
            "last_message": last_msg,
        })
    return result
