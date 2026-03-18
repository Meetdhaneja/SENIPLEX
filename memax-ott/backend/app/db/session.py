"""Database session management"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Generator, Optional

# Optimized for Render Free Tier (Low memory, low conn limits)
database_url = settings.sync_database_url
connect_args = {}
if database_url.startswith("postgresql://"):
    connect_args["connect_timeout"] = 15

engine = create_engine(
    database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=5,        # Small pool for Free Tier
    max_overflow=0,     # No overflow to stay within limits
    pool_timeout=15,    # Fail fast
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Optional[Session], None, None]:
    """Get database session with robust lifecycle management"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
