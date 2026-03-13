"""Initialize database tables"""
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.movie import Movie
from app.models.genre import Genre
from app.models.country import Country
from app.models.watch_history import WatchHistory
from app.models.watch_progress import WatchProgress
from app.models.interaction import Interaction
from app.models.user_features import UserFeatures
from app.models.movie_embeddings import MovieEmbedding
from app.models.recommendation_log import RecommendationLog
from loguru import logger


def init_db():
    """Create all database tables and handle schema updates"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Primitive migration: Check for missing columns and add them
        # (This is a simplified approach for Render deployments without Alembic migrations setup)
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check for age_rating
            try:
                conn.execute(text("SELECT age_rating FROM movies LIMIT 1"))
            except Exception:
                logger.info("Adding missing column 'age_rating' to movies table")
                conn.execute(text("ALTER TABLE movies ADD COLUMN age_rating VARCHAR(50)"))
                conn.commit()

            # Check for date_added
            try:
                conn.execute(text("SELECT date_added FROM movies LIMIT 1"))
            except Exception:
                logger.info("Adding missing column 'date_added' to movies table")
                conn.execute(text("ALTER TABLE movies ADD COLUMN date_added VARCHAR(100)"))
                conn.commit()
                
        logger.info("Database synchronized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # We don't raise here to let the app try to start anyway
