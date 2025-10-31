import redis
import json
import os
from typing import Optional, Any, List, Dict
from datetime import datetime, timedelta
import logging
import dotenv
dotenv.load_dotenv()

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis with proper configuration for development"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST'),
                port=int(os.getenv('REDIS_PORT')),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD', None),
                socket_connect_timeout=5, 
                socket_timeout=5,        
                # retry_on_timeout=True,
                decode_responses=True    
            )
            
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
            
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.warning("Running without cache - install Redis for better performance")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Redis error: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _make_cache_key(self, metric: str, start_time: str, end_time: str, 
                       aggregation: Optional[str] = None, interval: Optional[str] = None) -> str:
        """Create a unique cache key for query parameters"""
        base_key = f"timeseries:query:{metric}:{start_time}:{end_time}"
        if aggregation and interval:
            base_key += f":{aggregation}:{interval}"
        return base_key
    
    def get_cached_query(self, metric: str, start_time: str, end_time: str,
                        aggregation: Optional[str] = None, interval: Optional[str] = None) -> Optional[List[Dict]]:
        """Get cached query results"""
        if not self.is_connected():
            return None
            
        cache_key = self._make_cache_key(metric, start_time, end_time, aggregation, interval)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"Cache miss for key: {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set_cached_query(self, metric: str, start_time: str, end_time: str,
                        data: List[Dict], aggregation: Optional[str] = None, 
                        interval: Optional[str] = None, ttl_seconds: int = 300) -> None:
        """Cache query results"""
        if not self.is_connected():
            return
            
        cache_key = self._make_cache_key(metric, start_time, end_time, aggregation, interval)
        
        try:
            self.redis_client.setex(
                cache_key,
                timedelta(seconds=ttl_seconds),
                json.dumps(data, default=str)
            )
            logger.debug(f"Cached data for key: {cache_key} (TTL: {ttl_seconds}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def invalidate_metric_cache(self, metric: str) -> None:
        """Invalidate all cache entries for a specific metric"""
        if not self.is_connected():
            return
            
        try:
            pattern = f"timeseries:query:{metric}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.debug(f"Invalidated cache for metric: {metric} ({len(keys)} keys)")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cache (careful with this in production!)"""
        if not self.is_connected():
            return
            
        try:
            pattern = "timeseries:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared all cache ({len(keys)} keys)")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics and info"""
        if not self.is_connected():
            return {"status": "disconnected"}
            
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get('used_memory_human', 'N/A'),
                "connected_clients": info.get('connected_clients', 'N/A'),
                "keyspace_hits": info.get('keyspace_hits', 'N/A'),
                "keyspace_misses": info.get('keyspace_misses', 'N/A')
            }
        except Exception as e:
            return {"status": f"error: {str(e)}"}

cache_manager = CacheManager()