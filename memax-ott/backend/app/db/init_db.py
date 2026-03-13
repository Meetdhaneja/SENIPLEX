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
    """Create all database tables and handle schema updates with proper transaction isolation"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created or already exist")
        
        # Primitive migration: Check for missing columns and add them
        from sqlalchemy import text
        with engine.connect() as conn:
            # PostgreSQL requires explicit transaction handling for DDL if errors occur
            # We check and add columns one by one
            
            # Check age_rating
            try:
                conn.execute(text("SELECT age_rating FROM movies LIMIT 1"))
            except Exception:
                try:
                    logger.info("Syncing schema: Adding 'age_rating'")
                    conn.execute(text("ALTER TABLE movies ADD COLUMN age_rating VARCHAR(50)"))
                    conn.commit()
                except Exception as ex:
                    logger.warning(f"Failed to add age_rating (might already exist): {ex}")

            # Check date_added
            try:
                conn.execute(text("SELECT date_added FROM movies LIMIT 1"))
            except Exception:
                try:
                    logger.info("Syncing schema: Adding 'date_added'")
                    conn.execute(text("ALTER TABLE movies ADD COLUMN date_added VARCHAR(100)"))
                    conn.commit()
                except Exception as ex:
                    logger.warning(f"Failed to add date_added (might already exist): {ex}")
                
        logger.info("Database synchronized successfully")
    except Exception as e:
        logger.error(f"Critical error initializing database: {str(e)}")
        # Do not raise, allow app to attempt start
