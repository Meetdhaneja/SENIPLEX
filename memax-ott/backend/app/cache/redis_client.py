"""
Redis Cache Client
Caching layer for recommendations and features
"""
import json
import redis
from typing import Optional, Any, List
from loguru import logger
from app.core.config import settings


class RedisClient:
    """Redis client for caching"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            # Get Redis settings with fallbacks
            redis_host = getattr(settings, 'REDIS_HOST', 'localhost')
            redis_port = getattr(settings, 'REDIS_PORT', 6379)
            redis_db = getattr(settings, 'REDIS_DB', 0)
            
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            self.redis = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache: {str(e)}")
            return False
    
    def get_recommendations(self, user_id: int) -> Optional[List[int]]:
        """Get cached recommendations for user"""
        key = f"recommendations:user:{user_id}"
        return self.get(key)
    
    def set_recommendations(
        self,
        user_id: int,
        movie_ids: List[int],
        ttl: int = 1800
    ) -> bool:
        """Cache recommendations for user"""
        key = f"recommendations:user:{user_id}"
        return self.set(key, movie_ids, ttl)
    
    def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate all cache for user"""
        pattern = f"*:user:{user_id}*"
        try:
            if self.redis:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return False


# Global cache instance
_cache_instance: Optional[RedisClient] = None


def get_cache() -> RedisClient:
    """Get or create global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisClient()
    return _cache_instance


def get_redis_client() -> RedisClient:
    """Alias for get_cache() - for compatibility"""
    return get_cache()
