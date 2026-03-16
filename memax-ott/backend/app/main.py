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
    debug=settings.DEBUG,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Global Error Handler (Internal to app for better control)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Global catch: {str(exc)}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__,
            "traceback": tb # Enabled for debugging phase
        }
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else [],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Mount static
try:
    if os.path.exists("app/static"):
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
except: pass

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
    logger.info(f"Startup: {settings.ENVIRONMENT}")
    
    # Non-blocking background startup for Render Free Tier
    import threading
    from app.db.init_db import init_db
    
    def background_task():
        try:
            # 1. Init DB tables if they don't exist
            init_db()
            
            # List of columns to check and add if missing
            migrations = [
                ("age_rating", "VARCHAR(50)"),
                ("date_added", "VARCHAR(100)"),
                ("is_featured", "BOOLEAN DEFAULT FALSE"),
                ("view_count", "INTEGER DEFAULT 0"),
                ("rating", "FLOAT DEFAULT 0.0"),
                ("imdb_rating", "FLOAT"),
                ("thumbnail_url", "VARCHAR(500)"),
                ("is_active", "BOOLEAN DEFAULT TRUE")
            ]
            
            from sqlalchemy import text
            from app.db.session import SessionLocal
            
            db = SessionLocal()
            conn = db.connection()
            
            for col_name, col_type in migrations:
                try:
                    conn.execute(text(f"SELECT {col_name} FROM movies LIMIT 1"))
                except Exception:
                    try:
                        logger.info(f"Syncing schema: Adding column '{col_name}' to 'movies' table")
                        # PostgreSQL: Wrap in sub-transaction-like logic by committing if possible
                        conn.execute(text(f"ALTER TABLE movies ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"Successfully added {col_name}")
                    except Exception as ex:
                        logger.warning(f"Failed to add {col_name} (might require manual fix): {ex}")
            db.close()
            logger.info("Database migration/sync check complete")
            
            # 2. Seed only if empty and NOT in a tiny environment (Optional)
            if os.getenv("ENVIRONMENT") == "production":
                logger.info("Production mode: Skipping automated heavy seeding to conserve RAM. Seed manually via /api/admin/seed if needed.")
            else:
                from app.db.seed import seed_database
                seed_database()
        except Exception as e:
            logger.error(f"Background thread error: {e}")

    threading.Thread(target=background_task, daemon=True).start()

@app.get("/api/health/db-status")
async def db_status():
    from app.db.session import SessionLocal
    from app.models.movie import Movie
    db = SessionLocal()
    try:
        count = db.query(Movie).count()
        return {"status": "ready" if count > 0 else "empty", "count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.get("/")
async def root():
    return {"status": "online", "service": settings.APP_NAME}
