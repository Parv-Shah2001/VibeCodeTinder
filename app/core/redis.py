"""
Redis client abstraction with in-memory fallback for local dev without Redis.
Used for:
- Rate limiting (swipes, messages)
- Recommendation cache
- Online presence
- Swipe deduplication / Bloom filter simulation
- WebSocket pub/sub for messaging scale-out
"""
import json
import time
from typing import Any, Optional
from functools import lru_cache

from .config import settings

try:
    import redis  # type: ignore
    _redis_available = True
except ImportError:
    _redis_available = False

class InMemoryRedis:
    """Simplistic in-memory Redis fallback for dev/demo."""
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        if key in self._expiry and time.time() > self._expiry[key]:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    def get(self, key: str) -> Optional[str]:
        if self._is_expired(key):
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._store[key] = value if isinstance(value, str) else json.dumps(value)
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    def setex(self, key: str, ttl: int, value: Any) -> bool:
        return self.set(key, value, ex=ttl)

    def delete(self, *keys: str) -> int:
        count = 0
        for k in keys:
            if k in self._store:
                self._store.pop(k)
                self._expiry.pop(k, None)
                count += 1
        return count

    def exists(self, key: str) -> int:
        if self._is_expired(key):
            return 0
        return 1 if key in self._store else 0

    def incr(self, key: str) -> int:
        val = self._store.get(key, 0)
        try:
            val = int(val) + 1
        except:
            val = 1
        self._store[key] = str(val)
        return val

    def expire(self, key: str, ttl: int) -> bool:
        if key in self._store:
            self._expiry[key] = time.time() + ttl
            return True
        return False

    def sadd(self, key: str, *values: Any) -> int:
        s = self._store.get(key)
        if s is None:
            s = set()
        elif isinstance(s, str):
            try:
                s = set(json.loads(s))
            except:
                s = set()
        for v in values:
            s.add(v)
        self._store[key] = json.dumps(list(s))
        return len(s)

    def sismember(self, key: str, value: Any) -> bool:
        raw = self._store.get(key)
        if not raw:
            return False
        try:
            arr = json.loads(raw)
            return value in arr
        except:
            return False

    def zadd(self, key: str, mapping: dict) -> int:
        current = self._store.get(key)
        if current is None:
            current = {}
        elif isinstance(current, str):
            current = json.loads(current)
        current.update(mapping)
        self._store[key] = json.dumps(current)
        return len(mapping)

    def zrevrange(self, key: str, start: int, stop: int):
        raw = self._store.get(key)
        if not raw:
            return []
        try:
            data = json.loads(raw)
            sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
            sliced = sorted_items[start : stop + 1 if stop != -1 else None]
            return [k for k, _ in sliced]
        except:
            return []

    def pipeline(self):
        # dummy pipeline that executes immediately
        return self

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self): return True

    def publish(self, channel: str, message: str) -> int:
        return 0

    def pubsub(self):
        class DummyPubSub:
            def subscribe(self, *a, **kw): pass
            def get_message(self, *a, **kw): return None
        return DummyPubSub()


class RedisClient:
    def __init__(self):
        self._fallback = InMemoryRedis()
        self._client = None
        if _redis_available:
            try:
                self._client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
                self._client.ping()
            except Exception:
                self._client = None

    @property
    def client(self):
        return self._client if self._client else self._fallback

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex)

    def setex(self, key: str, ttl: int, value: Any):
        return self.set(key, value, ex=ttl)

    def delete(self, *keys: str):
        return self.client.delete(*keys)

    def exists(self, key: str):
        return self.client.exists(key)

    def incr(self, key: str):
        return self.client.incr(key)

    def expire(self, key: str, ttl: int):
        return self.client.expire(key, ttl)

    def sadd(self, key: str, *values):
        return self.client.sadd(key, *values)

    def sismember(self, key: str, value):
        return self.client.sismember(key, value)

    def zadd(self, key: str, mapping: dict):
        return self.client.zadd(key, mapping)

    def zrevrange(self, key: str, start: int, stop: int):
        return self.client.zrevrange(key, start, stop)

    def publish(self, channel: str, message: str):
        try:
            return self.client.publish(channel, message)
        except:
            return 0

@lru_cache()
def get_redis() -> RedisClient:
    return RedisClient()

redis_client = get_redis()
