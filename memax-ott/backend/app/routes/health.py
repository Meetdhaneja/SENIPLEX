"""
Health Check Route
System health and status monitoring
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from pathlib import Path

from app.db.session import get_db
from loguru import logger

router = APIRouter()


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """
    Health Check Endpoint
    Returns system health status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MEMAX OTT Backend",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check AI system
    try:
        index_path = Path("app/ai/faiss/index_store/memax_movie.index")
        if index_path.exists():
            health_status["checks"]["ai_system"] = {
                "status": "active",
                "message": "AI recommendation system is active",
                "index_size_kb": round(index_path.stat().st_size / 1024, 2)
            }
        else:
            health_status["checks"]["ai_system"] = {
                "status": "inactive",
                "message": "AI system not activated (using fallback mode)"
            }
    except Exception as e:
        health_status["checks"]["ai_system"] = {
            "status": "error",
            "message": f"AI system check failed: {str(e)}"
        }
        logger.error(f"AI system health check failed: {str(e)}")
    
    # Check API
    health_status["checks"]["api"] = {
        "status": "healthy",
        "message": "API is responding"
    }
    
    return health_status
