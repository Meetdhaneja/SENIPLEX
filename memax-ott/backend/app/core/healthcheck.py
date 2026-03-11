"""Health check endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.cache.redis_client import get_redis_client
import redis

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "MEMAX OTT"}


@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@router.get("/health/redis")
async def redis_health():
    """Redis health check"""
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}
