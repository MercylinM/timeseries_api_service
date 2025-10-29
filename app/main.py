import os
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from typing import Dict, Any
import dotenv
dotenv.load_dotenv()

limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["100/minute"], 
    storage_uri=f"redis://{os.getenv('REDIS_HOST')}:6379"
)

app = FastAPI(
    title="Super-Simple Timeseries API",
    description="A lightweight time-series data storage and query service",
    version="1.0.0"
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from routes.ingest import router as ingest_router
from routes.query import router as query_router
from routes.metrics import router as metrics_router
from routes.cache import router as cache_router

from database import init_db
from utils.cache import cache_manager

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    if cache_manager.is_connected():
        print("Redis cache connected successfully!")
    else:
        print("Redis cache NOT connected - running without caching")

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(metrics_router)
app.include_router(cache_router)

@app.get("/")
async def root() -> Dict[str, str]:
    redis_status = "connected" if cache_manager.is_connected() else "disconnected"
    return {
        "message": "Super-Simple Timeseries API Service",
        "version": "1.0.0",
        "redis_status": redis_status,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    redis_status = "healthy" if cache_manager.is_connected() else "unhealthy"
    return {
        "status": "healthy",
        "redis": redis_status,
        "database": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)