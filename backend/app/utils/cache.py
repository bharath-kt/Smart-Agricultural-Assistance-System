"""Redis cache utilities."""
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any, Union
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and date objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

logger = get_logger(__name__)


class CacheManager:
    """Redis cache manager with fallback when Redis is unavailable."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._available: bool = True
    
    async def connect(self):
        """Connect to Redis."""
        if self._redis is None and self._available:
            try:
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                await self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable, caching disabled: {e}")
                self._available = False
                self._redis = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
            self._redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self._available:
            return None
        await self.connect()
        if not self._redis:
            return None
        try:
            return await self._redis.get(key)
        except Exception:
            return None
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, bytes], 
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration."""
        if not self._available:
            return False
        await self.connect()
        if not self._redis:
            return False
        try:
            return await self._redis.set(key, value, ex=expire)
        except Exception:
            return False
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        expire: int = 3600
    ) -> bool:
        """Set JSON value in cache."""
        return await self.set(key, json.dumps(value, cls=DateTimeEncoder), expire)
    
    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        if not self._available:
            return 0
        await self.connect()
        if not self._redis:
            return 0
        try:
            return await self._redis.delete(key)
        except Exception:
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._available:
            return False
        await self.connect()
        if not self._redis:
            return False
        try:
            return await self._redis.exists(key) > 0
        except Exception:
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        if not self._available:
            return 0
        await self.connect()
        if not self._redis:
            return 0
        try:
            return await self._redis.incr(key, amount)
        except Exception:
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        if not self._available:
            return False
        await self.connect()
        if not self._redis:
            return False
        try:
            return await self._redis.expire(key, seconds)
        except Exception:
            return False
    
    async def get_rate_limit(self, key: str, window: int, max_requests: int) -> tuple:
        """Check rate limit."""
        if not self._available:
            # Allow all requests when Redis is unavailable
            return True, 0, window
        await self.connect()
        if not self._redis:
            return True, 0, window
        try:
            current = await self._redis.get(key)
            
            if current is None:
                await self._redis.set(key, 1, ex=window)
                return True, 1, window
            
            current = int(current)
            if current >= max_requests:
                ttl = await self._redis.ttl(key)
                return False, current, ttl
            
            await self._redis.incr(key)
            return True, current + 1, window
        except Exception:
            return True, 0, window


# Global cache instance
cache = CacheManager()
