"""
Caching utilities for MarketPulse application.
Provides in-memory caching with TTL support.
"""
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import threading

from config import config
from utils.logging_config import get_logger

logger = get_logger(__name__)


class MemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if time.time() > entry['expires_at']:
                del self._cache[key]
                return None

            logger.debug("Cache hit", key=key)
            return entry['value']

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = config.cache.default_ttl

        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            logger.debug("Cache set", key=key, ttl=ttl)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("Cache delete", key=key)
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info("Cache cleared", entries_removed=count)

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry['expires_at']
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug("Expired cache entries removed", count=len(expired_keys))

            return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            active_entries = sum(
                1 for entry in self._cache.values()
                if current_time <= entry['expires_at']
            )
            expired_entries = len(self._cache) - active_entries

            return {
                'total_entries': len(self._cache),
                'active_entries': active_entries,
                'expired_entries': expired_entries
            }


# Global cache instance
cache = MemoryCache()


def cached(ttl: int = None, key_func: Callable = None):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            logger.debug("Cache miss, executing function", function=func.__name__, key=cache_key)
            result = func(*args, **kwargs)

            if result is not None:  # Only cache non-None results
                cache.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def cache_key_for_symbol(symbol: str, data_type: str = "stock") -> str:
    """Generate cache key for symbol data."""
    return f"symbol:{data_type}:{symbol.upper()}"


def cache_key_for_news(source: str = "all", limit: int = 10) -> str:
    """Generate cache key for news data."""
    return f"news:{source}:{limit}"


def cache_key_for_analysis(symbol: str, analysis_type: str) -> str:
    """Generate cache key for analysis results."""
    return f"analysis:{analysis_type}:{symbol.upper()}"


# Periodic cleanup function (can be called by a background task)
def periodic_cleanup():
    """Clean up expired cache entries."""
    removed = cache.cleanup_expired()
    if removed > 0:
        logger.info("Periodic cache cleanup completed", entries_removed=removed)
    return removed
