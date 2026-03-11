"""
Async Task: Log Recommendations
Background task to log recommendation events
"""
from datetime import datetime
from typing import List
from loguru import logger
from app.db.session import SessionLocal
from app.models.recommendation_log import RecommendationLog


def log_recommendation_task(
    user_id: int,
    movie_ids: List[int],
    algorithm: str = 'hybrid',
    context: dict = None
):
    """
    Log recommendation event
    
    Args:
        user_id: User ID
        movie_ids: List of recommended movie IDs
        algorithm: Algorithm used
        context: Optional context dict
    """
    db = SessionLocal()
    
    try:
        # Create log entries
        for position, movie_id in enumerate(movie_ids):
            log_entry = RecommendationLog(
                user_id=user_id,
                movie_id=movie_id,
                algorithm=algorithm,
                position=position,
                context=context,
                created_at=datetime.utcnow()
            )
            db.add(log_entry)
        
        db.commit()
        logger.debug(f"Logged {len(movie_ids)} recommendations for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error logging recommendations: {str(e)}")
        db.rollback()
    finally:
        db.close()


def log_recommendation_click_task(
    user_id: int,
    movie_id: int,
    position: int
):
    """
    Log when user clicks on a recommendation
    
    Args:
        user_id: User ID
        movie_id: Movie ID clicked
        position: Position in recommendation list
    """
    db = SessionLocal()
    
    try:
        # Find the recommendation log
        log_entry = db.query(RecommendationLog).filter(
            RecommendationLog.user_id == user_id,
            RecommendationLog.movie_id == movie_id,
            RecommendationLog.clicked_at.is_(None)
        ).order_by(
            RecommendationLog.created_at.desc()
        ).first()
        
        if log_entry:
            log_entry.clicked_at = datetime.utcnow()
            log_entry.was_clicked = True
            db.commit()
            logger.debug(f"Logged click for user {user_id}, movie {movie_id}")
        
    except Exception as e:
        logger.error(f"Error logging click: {str(e)}")
        db.rollback()
    finally:
        db.close()


def log_recommendation_conversion_task(
    user_id: int,
    movie_id: int,
    watch_duration: float = None
):
    """
    Log when user watches a recommended movie
    
    Args:
        user_id: User ID
        movie_id: Movie ID watched
        watch_duration: Duration watched in seconds
    """
    db = SessionLocal()
    
    try:
        # Find the recommendation log
        log_entry = db.query(RecommendationLog).filter(
            RecommendationLog.user_id == user_id,
            RecommendationLog.movie_id == movie_id,
            RecommendationLog.converted_at.is_(None)
        ).order_by(
            RecommendationLog.created_at.desc()
        ).first()
        
        if log_entry:
            log_entry.converted_at = datetime.utcnow()
            log_entry.was_converted = True
            if watch_duration:
                log_entry.watch_duration = watch_duration
            db.commit()
            logger.debug(f"Logged conversion for user {user_id}, movie {movie_id}")
        
    except Exception as e:
        logger.error(f"Error logging conversion: {str(e)}")
        db.rollback()
    finally:
        db.close()


def batch_log_recommendations_task(recommendations_batch: list):
    """
    Log multiple recommendation events in batch
    
    Args:
        recommendations_batch: List of dicts with user_id, movie_ids, algorithm
    """
    for rec in recommendations_batch:
        try:
            log_recommendation_task(
                user_id=rec['user_id'],
                movie_ids=rec['movie_ids'],
                algorithm=rec.get('algorithm', 'hybrid'),
                context=rec.get('context')
            )
        except Exception as e:
            logger.error(f"Error in batch logging: {str(e)}")
            continue
