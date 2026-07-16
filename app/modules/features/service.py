"""
Feature flag service + A/B testing framework.
For 1M DAU we need gradual rollout + experimentation.

In production would use LaunchDarkly / Unleash / internal service with Redis.
For monolith: simple JSON config + user_id hash bucketing.
"""
import hashlib
from app.core.redis import redis_client
import json

# Default flags
DEFAULT_FLAGS = {
    "new_discovery_algorithm": {"enabled": True, "rollout": 50, "description": "New ML ranking vs old Elo"},
    "video_profiles": {"enabled": False, "rollout": 10, "description": "Allow video upload in profile"},
    "voice_messages": {"enabled": False, "rollout": 20},
    "super_boost": {"enabled": True, "rollout": 100},
    "explore_tab": {"enabled": True, "rollout": 100},
    "likes_you": {"enabled": True, "rollout": 100},
}

def get_flag(name: str, user_id: int) -> bool:
    try:
        # Check Redis override
        override = redis_client.get(f"feature:{name}")
        if override:
            data = json.loads(override)
            # Could have per-user overrides
            pass
    except Exception:
        pass

    flag = DEFAULT_FLAGS.get(name)
    if not flag:
        return False
    if not flag["enabled"]:
        return False
    rollout = flag["rollout"]
    if rollout >= 100:
        return True
    # Hash bucketing
    h = int(hashlib.md5(f"{name}:{user_id}".encode()).hexdigest()[:8], 16)
    bucket = h % 100
    return bucket < rollout

def get_all_flags(user_id: int) -> dict:
    return {name: get_flag(name, user_id) for name in DEFAULT_FLAGS}

def set_flag(name: str, enabled: bool, rollout: int = 100):
    try:
        redis_client.set(f"feature:{name}", json.dumps({"enabled": enabled, "rollout": rollout}))
    except Exception:
        pass
    if name in DEFAULT_FLAGS:
        DEFAULT_FLAGS[name]["enabled"] = enabled
        DEFAULT_FLAGS[name]["rollout"] = rollout
