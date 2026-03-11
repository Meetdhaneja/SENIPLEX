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
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
