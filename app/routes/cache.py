from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from utils.cache import cache_manager
from main import limiter 

router = APIRouter(prefix="/cache", tags=["cache"])

@router.get("/info")
@limiter.limit("60/minute")
async def get_cache_info(request: Request) -> Dict[str, Any]:
    """
    Get Redis cache information and statistics
    
    Returns:
    - Redis connection status
    - Cache hit rates
    - Memory usage
    - Number of cached keys
    """
    return cache_manager.get_cache_info()

@router.post("/clear")
@limiter.limit("10/minute") 
async def clear_cache(request: Request) -> Dict[str, str]:
    """
    Clear all cache
    This will remove all cached query results.
    """
    cache_manager.clear_cache()
    return {"message": "Cache cleared successfully"}

@router.post("/metrics/{metric}/clear")
async def clear_metric_cache(request: Request,metric: str) -> Dict[str, str]:
    """
    Clear cache for a specific metric
    
    Requires the metric name to clear from cache
    """
    cache_manager.invalidate_metric_cache(metric)
    return {"message": f"Cache cleared for metric: {metric}"}

@router.get("/keys")
@limiter.limit("30/minute") 
async def list_cache_keys(request: Request) -> Dict[str, Any]:
    """
    List all cache keys matching the timeseries pattern
    
    Returns all keys matching the timeseries pattern.
    """
    if not cache_manager.is_connected():
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    try:
        pattern = "ts:*"
        keys = cache_manager.redis_client.keys(pattern)
        return {
            "count": len(keys),
            "keys": keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing keys: {str(e)}")
    
