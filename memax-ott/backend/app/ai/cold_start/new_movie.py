"""
Cold Start - New Movie Recommendations
Handle recommendations for newly added movies
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from app.models.movie import Movie
from app.models.movie_embeddings import MovieEmbedding
from app.ai.faiss.search import get_search_instance


class NewMovieRecommender:
    """Generate recommendations for newly added movies"""
    
    def __init__(self):
        self.similarity_threshold = 0.7
    
    def get_similar_movies(
        self,
        movie_id: int,
        db: Session,
        count: int = 10
    ) -> List[int]:
        """
        Get similar movies for a new movie
        
        Args:
            movie_id: New movie ID
            db: Database session
            count: Number of similar movies to return
        
        Returns:
            List of similar movie IDs
        """
        try:
            # Get movie
            movie = db.query(Movie).filter(Movie.id == movie_id).first()
            if not movie:
                return []
            
            # Try embedding-based similarity first
            embedding_data = db.query(MovieEmbedding).filter(
                MovieEmbedding.movie_id == movie_id
            ).first()
            
            if embedding_data and embedding_data.content_embedding:
                # Use FAISS search
                embedding = np.frombuffer(embedding_data.content_embedding, dtype=np.float32)
                searcher = get_search_instance()
                similar = searcher.search_similar(embedding, k=count, exclude_ids=[movie_id])
                return [mid for mid, _ in similar]
            
            # Fallback to genre-based similarity
            return self._get_genre_based_similar(movie, db, count)
            
        except Exception as e:
            logger.error(f"Error getting similar movies for new movie: {str(e)}")
            return []
    
    def _get_genre_based_similar(
        self,
        movie: Movie,
        db: Session,
        count: int
    ) -> List[int]:
        """Get similar movies based on genres"""
        try:
            if not movie.genres:
                return []
            
            genre_ids = [g.id for g in movie.genres]
            
            # Find movies with overlapping genres
            similar_movies = db.query(Movie).join(Movie.genres).filter(
                Movie.id != movie.id,
                Movie.is_active == True,
                Movie.genres.any(id__in=genre_ids)
            ).order_by(
                desc(Movie.rating)
            ).limit(count).all()
            
            return [m.id for m in similar_movies]
            
        except Exception as e:
            logger.error(f"Error in genre-based similarity: {str(e)}")
            return []
    
    def get_target_audience(
        self,
        movie_id: int,
        db: Session,
        count: int = 100
    ) -> List[int]:
        """
        Get potential target audience (user IDs) for a new movie
        
        Args:
            movie_id: New movie ID
            db: Database session
            count: Number of users to target
        
        Returns:
            List of user IDs
        """
        try:
            from app.models.user import User
            from app.models.interaction import Interaction
            
            # Get movie
            movie = db.query(Movie).filter(Movie.id == movie_id).first()
            if not movie:
                return []
            
            # Find users who liked similar movies
            similar_movie_ids = self.get_similar_movies(movie_id, db, count=20)
            
            if similar_movie_ids:
                # Get users who interacted with similar movies
                target_users = db.query(Interaction.user_id).filter(
                    Interaction.movie_id.in_(similar_movie_ids),
                    Interaction.interaction_type.in_(['view', 'like', 'complete'])
                ).group_by(
                    Interaction.user_id
                ).limit(count).all()
                
                return [user_id for user_id, in target_users]
            
            # Fallback: users who like this genre
            if movie.genres:
                genre_ids = [g.id for g in movie.genres]
                
                target_users = db.query(Interaction.user_id).join(
                    Movie
                ).join(
                    Movie.genres
                ).filter(
                    Movie.genres.any(id__in=genre_ids)
                ).group_by(
                    Interaction.user_id
                ).limit(count).all()
                
                return [user_id for user_id, in target_users]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting target audience: {str(e)}")
            return []
    
    def boost_new_movie(
        self,
        movie_id: int,
        boost_duration_days: int = 7
    ) -> dict:
        """
        Create boost configuration for new movie
        
        Args:
            movie_id: New movie ID
            boost_duration_days: How long to boost the movie
        
        Returns:
            Dict with boost configuration
        """
        return {
            'movie_id': movie_id,
            'boost_factor': 1.5,
            'boost_until': datetime.utcnow() + timedelta(days=boost_duration_days),
            'boost_type': 'new_content'
        }


def recommend_new_movie_to_users(
    movie_id: int,
    db: Session,
    max_users: int = 100
) -> List[int]:
    """
    Get list of users to recommend a new movie to
    
    Args:
        movie_id: New movie ID
        db: Database session
        max_users: Maximum number of users to target
    
    Returns:
        List of user IDs
    """
    recommender = NewMovieRecommender()
    return recommender.get_target_audience(movie_id, db, max_users)
