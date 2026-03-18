"""MEMAX OTT Platform - Main Application Entry Point"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sys
import traceback
import os
import time

from app.core.config import settings
from app.core.middleware import LoggingMiddleware
from app.core.rate_limiter import limiter
from app.core.healthcheck import router as health_router
from app.routes import auth, movies, interactions, recommendations, analytics, admin, ai, likes, health

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=True,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# ─── ULTIMATE SAFETY MIDDLEWARE ──────────────────────────────────────────
# This catches errors that occur EVEN BEFORE they reach our routes or 
# exception handlers (like in other middlewares or pydantic validation).
@app.middleware("http")
async def ultimate_safety_middleware(request: Request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"FATAL REQUEST ERROR: {request.url.path}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Fatal Backend Error",
                "message": str(e),
                "path": request.url.path,
                "traceback": tb
            }
        )

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"FastAPI Exception: {str(exc)}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": str(exc),
            "traceback": tb 
        }
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Extreme flexibility for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(health.router, prefix="/api/health-check", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["Interactions"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recs"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(likes.router, prefix="/api/likes", tags=["Likes"])

@app.on_event("startup")
async def startup_event():
    """Ultra-Lean Startup to prevent OOM on Render Free Tier"""
    logger.info(f"App Starting in {settings.ENVIRONMENT} mode")
    
    # DO NOT RUN MIGRATIONS OR SEEDING AUTOMATICALLY ON STARTUP
    # This prevents the initial RAM spike that causes Render kills.
    # Seeding can be triggered manually via /api/admin/seed if needed.
    logger.info("Automatic migrations and seeding DISABLED to conserve memory.")

@app.get("/api/ping")
async def ping():
    return {"status": "pong", "time": time.time(), "env": os.getenv("ENVIRONMENT")}

@app.get("/")
async def root():
    return {
        "status": "online", 
        "service": settings.APP_NAME,
        "api_docs": "/api/docs",
        "api_ping": "/api/ping",
        "env": os.getenv("ENVIRONMENT")
    }
