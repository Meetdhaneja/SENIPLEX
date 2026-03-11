"""Build user embeddings"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.user_features import UserFeatures
from app.models.interaction import Interaction
from app.models.movie_embeddings import MovieEmbedding
import numpy as np
from loguru import logger


def build_user_embedding(user_id: int, db: Session) -> list:
    """Build embedding for a user based on their interactions"""
    # Get user interactions
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    
    if not interactions:
        return None
    
    # Get movie embeddings for interacted movies
    movie_ids = [i.movie_id for i in interactions]
    movie_embeddings = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id.in_(movie_ids)).all()
    
    if not movie_embeddings:
        return None
    
    # Weighted average of movie embeddings
    embeddings = []
    weights = []
    
    # Define interaction weights
    interaction_weights = {
        "like": 2.0,
        "watch_later": 1.5,
        "view": 1.0,
        "search_click": 1.2,
        "dislike": -1.5
    }
    
    for interaction in interactions:
        movie_emb = next((me for me in movie_embeddings if me.movie_id == interaction.movie_id), None)
        if movie_emb and movie_emb.content_embedding:
            base_weight = interaction_weights.get(interaction.interaction_type, interaction.interaction_value)
            
            # If it's a strongly negative weight (dislike), we subtract the vector, so mathematically we use negative weight. 
            # However, numpy average requires positive weights for normalizing. 
            # To handle this, we can invert the vector for negative weights and use positive weight magnitude.
            weight_mag = abs(base_weight)
            
            vec = np.array(movie_emb.content_embedding)
            if base_weight < 0:
                vec = -vec
                
            embeddings.append(vec.tolist())
            weights.append(weight_mag)
    
    if not embeddings:
        return None
    
    # Calculate weighted average
    embeddings_array = np.array(embeddings)
    weights_array = np.array(weights).reshape(-1, 1)
    
    # Avoid zero division
    sum_weights = np.sum(weights_array)
    if sum_weights > 0:
        user_embedding = np.average(embeddings_array, axis=0, weights=weights_array.flatten())
    else:
        user_embedding = np.mean(embeddings_array, axis=0)
        
    # Normalize the output embedding to unit length (essential for cosine similarity)
    norm = np.linalg.norm(user_embedding)
    if norm > 0:
        user_embedding = user_embedding / norm
    
    return user_embedding.tolist()


def build_all_user_embeddings():
    """Build embeddings for all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Building embeddings for {len(users)} users")
        
        for user in users:
            embedding = build_user_embedding(user.id, db)
            if embedding:
                user_features = db.query(UserFeatures).filter(UserFeatures.user_id == user.id).first()
                if user_features:
                    user_features.user_embedding = embedding
                    db.commit()
        
        logger.info("User embeddings built successfully")
    except Exception as e:
        logger.error(f"Error building user embeddings: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    build_all_user_embeddings()
