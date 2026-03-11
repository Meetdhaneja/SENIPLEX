"""
Async Task: Rebuild FAISS Index
Background task to rebuild FAISS index
"""
from loguru import logger
from app.ai.faiss.build_index import FAISSIndexBuilder


def rebuild_faiss_index_task():
    """Rebuild FAISS index from scratch"""
    try:
        logger.info("Starting FAISS index rebuild")
        
        builder = FAISSIndexBuilder()
        success = builder.rebuild_index()
        
        if success:
            logger.info("FAISS index rebuild completed successfully")
        else:
            logger.error("FAISS index rebuild failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Error rebuilding FAISS index: {str(e)}")
        return False


def incremental_faiss_update_task(movie_ids: list):
    """
    Add new movies to FAISS index incrementally
    
    Args:
        movie_ids: List of new movie IDs to add
    """
    from app.db.session import SessionLocal
    from app.models.movie_embeddings import MovieEmbedding
    import numpy as np
    
    db = SessionLocal()
    
    try:
        logger.info(f"Adding {len(movie_ids)} movies to FAISS index")
        
        builder = FAISSIndexBuilder()
        builder.load_index()
        
        # Get embeddings for new movies
        embeddings_data = db.query(MovieEmbedding).filter(
            MovieEmbedding.movie_id.in_(movie_ids),
            MovieEmbedding.content_embedding.isnot(None)
        ).all()
        
        # Add each embedding
        for embedding_data in embeddings_data:
            embedding = np.frombuffer(
                embedding_data.content_embedding,
                dtype=np.float32
            )
            builder.add_movie_embedding(embedding_data.movie_id, embedding)
        
        logger.info(f"Successfully added {len(embeddings_data)} movies to index")
        
    except Exception as e:
        logger.error(f"Error in incremental FAISS update: {str(e)}")
    finally:
        db.close()


def schedule_faiss_rebuild(interval_hours: int = 24):
    """
    Schedule periodic FAISS index rebuilds
    
    Args:
        interval_hours: Hours between rebuilds
    """
    import time
    
    while True:
        try:
            rebuild_faiss_index_task()
            time.sleep(interval_hours * 3600)
        except Exception as e:
            logger.error(f"Error in scheduled rebuild: {str(e)}")
            time.sleep(3600)  # Wait 1 hour before retry
