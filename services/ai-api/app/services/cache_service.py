import hashlib
import json
from cachetools import TTLCache
from app.config import settings

_cache: TTLCache = TTLCache(maxsize=settings.cache_maxsize, ttl=settings.cache_ttl)


def make_key(prefix: str, params: dict) -> str:
    raw = json.dumps(params, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()
    return f"{prefix}:{digest}"


def get(key: str):
    return _cache.get(key)


def set(key: str, value) -> None:
    _cache[key] = value
