"""Database session management"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Generator, Optional

# Optimized for Render Free Tier (Low memory, low conn limits)
engine = create_engine(
    settings.sync_database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=5,        # Small pool for Free Tier
    max_overflow=0,     # No overflow to stay within limits
    pool_timeout=15,    # Fail fast
    connect_args={"connect_timeout": 15} # Fast connection fail
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Optional[Session], None, None]:
    """Get database session with robust error handling"""
    db = None
    try:
        db = SessionLocal()
        # Verify connection immediately, if it fails, yield None
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        from loguru import logger
        logger.warning(f"Database connection failed in get_db: {str(e)}")
        yield None
    finally:
        if db:
            db.close()
