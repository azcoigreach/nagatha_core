"""
Redis client factory and shared instance.

Provides factory functions for creating Redis clients and a singleton
pattern for accessing a shared Redis instance.
"""

from typing import Optional
import redis
from redis import Redis

from .settings import Settings, get_settings


def create_redis_client(settings: Optional[Settings] = None) -> Redis:
    """
    Create a Redis client from settings.
    
    Args:
        settings: Optional Settings instance (uses global settings if None)
        
    Returns:
        Redis client instance
        
    Example:
        >>> from nagatha_core.runtime import create_redis_client, Settings
        >>> settings = Settings(redis_url="redis://localhost:6379/1")
        >>> redis_client = create_redis_client(settings)
        >>> redis_client.ping()
        True
    """
    if settings is None:
        settings = get_settings()
    
    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
        encoding="utf-8",
    )


# Global Redis instance
_redis_instance: Optional[Redis] = None


def get_redis_instance() -> Redis:
    """
    Get or create the global Redis client instance.
    
    Returns:
        Shared Redis client
        
    Example:
        >>> from nagatha_core.runtime import get_redis_instance
        >>> redis_client = get_redis_instance()
        >>> redis_client.set("key", "value")
        >>> redis_client.get("key")
        'value'
    """
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = create_redis_client()
    return _redis_instance
