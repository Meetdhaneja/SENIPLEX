"""Database session management"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Generator, Optional

engine = create_engine(
    settings.sync_database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Optional[Session], None, None]:
    """Get database session with robust error handling"""
    db = None
    try:
        db = SessionLocal()
        # Verify connection immediately
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        from loguru import logger
        logger.warning(f"Database connection failed in get_db: {str(e)}")
        yield None
    finally:
        if db:
            db.close()
