"""Interaction service"""
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.interaction import Interaction
from app.models.watch_progress import WatchProgress
from app.models.watch_history import WatchHistory
from app.schemas.interaction_schema import InteractionCreate, WatchProgressCreate


from app.tasks.update_user_embedding import update_user_embedding_task

def create_interaction(db: Session, user_id: int, interaction_data: InteractionCreate) -> Interaction:
    """Create interaction"""
    interaction = Interaction(
        user_id=user_id,
        **interaction_data.dict()
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # Trigger AI matrix embedding update asynchronously via Celery
    try:
        update_user_embedding_task.delay(user_id)
    except Exception as e:
        import loguru
        loguru.logger.error(f"Failed to queue celery task: {str(e)}")
        
    return interaction


def get_user_interactions(db: Session, user_id: int, limit: int = 100) -> List[Interaction]:
    """Get user interactions"""
    return db.query(Interaction).filter(Interaction.user_id == user_id).order_by(Interaction.timestamp.desc()).limit(limit).all()


def create_or_update_watch_progress(db: Session, user_id: int, progress_data: WatchProgressCreate) -> WatchProgress:
    """Create or update watch progress"""
    progress = db.query(WatchProgress).filter(
        WatchProgress.user_id == user_id,
        WatchProgress.movie_id == progress_data.movie_id
    ).first()
    
    if progress:
        progress.progress_seconds = progress_data.progress_seconds
        progress.progress_percentage = progress_data.progress_percentage
        progress.last_watched_at = datetime.utcnow()
    else:
        progress = WatchProgress(
            user_id=user_id,
            **progress_data.dict()
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    return progress


def get_user_watch_progress(db: Session, user_id: int) -> List[WatchProgress]:
    """Get user watch progress"""
    return db.query(WatchProgress).filter(
        WatchProgress.user_id == user_id,
        WatchProgress.progress_percentage < 95
    ).order_by(WatchProgress.last_watched_at.desc()).all()
