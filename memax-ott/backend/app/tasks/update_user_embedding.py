"""
Async Task: Update User Embedding
Background task to update user embeddings
"""
from loguru import logger
from app.db.session import SessionLocal
from app.ai.embeddings.build_user_embeddings import build_user_embedding
from app.cache.redis_client import get_cache
from app.core.celery_app import celery_app

@celery_app.task(name="update_user_embedding")
def update_user_embedding_task(user_id: int):
    """
    Update embedding for a single user
    
    Args:
        user_id: User ID to update
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Updating embedding for user {user_id}")
        
        # Build user embedding
        build_user_embedding(user_id, db)
        
        # Invalidate cache
        cache = get_cache()
        cache.invalidate_user_cache(user_id)
        
        logger.info(f"Successfully updated embedding for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error updating user embedding: {str(e)}")
    finally:
        db.close()


def update_multiple_user_embeddings_task(user_ids: list):
    """
    Update embeddings for multiple users
    
    Args:
        user_ids: List of user IDs
    """
    logger.info(f"Updating embeddings for {len(user_ids)} users")
    
    for user_id in user_ids:
        try:
            update_user_embedding_task(user_id)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            continue
    
    logger.info("Batch user embedding update complete")


def update_all_user_embeddings_task():
    """Update embeddings for all active users"""
    from app.models.user import User
    
    db = SessionLocal()
    
    try:
        # Get all active users
        users = db.query(User.id).filter(User.is_active == True).all()
        user_ids = [user_id for user_id, in users]
        
        logger.info(f"Updating embeddings for {len(user_ids)} active users")
        update_multiple_user_embeddings_task(user_ids)
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
    finally:
        db.close()
