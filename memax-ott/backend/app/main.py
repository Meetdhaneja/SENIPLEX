"""MEMAX OTT Platform - Main Application Entry Point"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sys

from app.core.config import settings
from app.core.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.core.rate_limiter import limiter
from app.core.healthcheck import router as health_router
from app.routes import auth, movies, interactions, recommendations, analytics, admin, ai, likes, health
from app.db.init_db import init_db

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered OTT Platform with Personalized Recommendations",
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else [],
    allow_origin_regex=".*", # Allow all domains in production for Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except RuntimeError:
    logger.warning("Static directory not found, skipping static files mount")

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["Interactions"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(likes.router, prefix="/api/likes", tags=["Likes"])

# Admin UI
from app.admin_ui import routes as admin_ui_routes
app.include_router(admin_ui_routes.router, prefix="/admin", tags=["Admin UI"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Run DB Initialization and Seeding in background
    # This ensures the server starts listening on the port IMMEDIATELY
    import threading
    from app.db.seed import seed_database
    
    def background_startup():
        try:
            # Initialize database (schema checks/migrations)
            init_db()
            logger.info("Database initialized successfully in background")
            
            # Seed database
            seed_database()
            logger.info("Database seeding completed in background")
        except Exception as e:
            logger.error(f"Background startup task failed: {str(e)}")

    threading.Thread(target=background_startup, daemon=True).start()
    logger.info("Database initialization and seeding started in background thread")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.get("/api/health/db-status")
async def db_status():
    """Check database status and movie count"""
    from app.db.session import SessionLocal
    from app.models.movie import Movie
    db = SessionLocal()
    try:
        count = db.query(Movie).count()
        return {"movie_count": count, "status": "ok" if count > 0 else "seeding"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
