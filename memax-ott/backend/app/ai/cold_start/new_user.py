"""
Cold Start - New User Recommendations
Handle recommendations for users with no history
"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from loguru import logger

from app.models.movie import Movie
from app.models.genre import Genre
from app.models.interaction import Interaction


class NewUserRecommender:
    """Generate recommendations for new users"""
    
    def __init__(self):
        self.default_recommendations_count = 20
    
    def get_recommendations(
        self,
        db: Session,
        user_preferences: dict = None,
        count: int = 20
    ) -> List[int]:
        """
        Get recommendations for new user
        
        Args:
            db: Database session
            user_preferences: Optional dict with 'genres', 'min_rating', etc.
            count: Number of recommendations
        
        Returns:
            List of movie IDs
        """
        try:
            # Start with base query
            query = db.query(Movie).filter(Movie.is_active == True)
            
            # Apply user preferences if provided
            if user_preferences:
                # Genre filter
                if 'genres' in user_preferences and user_preferences['genres']:
                    query = query.join(Movie.genres).filter(
                        Genre.name.in_(user_preferences['genres'])
                    )
                
                # Rating filter
                if 'min_rating' in user_preferences:
                    query = query.filter(Movie.rating >= user_preferences['min_rating'])
                
                # Content type filter
                if 'content_type' in user_preferences:
                    query = query.filter(Movie.content_type == user_preferences['content_type'])
            
            # Get popular movies
            movies = query.order_by(
                desc(Movie.rating),
                desc(Movie.view_count)
            ).limit(count).all()
            
            return [m.id for m in movies]
            
        except Exception as e:
            logger.error(f"Error getting new user recommendations: {str(e)}")
            return self._get_fallback_recommendations(db, count)
    
    def get_onboarding_recommendations(
        self,
        db: Session,
        selected_genres: List[str] = None,
        count: int = 20
    ) -> List[int]:
        """
        Get recommendations based on onboarding genre selection
        
        Args:
            db: Database session
            selected_genres: List of genre names selected during onboarding
            count: Number of recommendations
        
        Returns:
            List of movie IDs
        """
        try:
            if not selected_genres:
                return self.get_trending_recommendations(db, count)
            
            # Get top movies from selected genres
            movies = db.query(Movie).join(Movie.genres).filter(
                Genre.name.in_(selected_genres),
                Movie.is_active == True
            ).order_by(
                desc(Movie.rating),
                desc(Movie.view_count)
            ).limit(count * 2).all()  # Get extra for diversity
            
            # Ensure diversity across genres
            result = []
            genre_counts = {genre: 0 for genre in selected_genres}
            max_per_genre = count // len(selected_genres) + 1
            
            for movie in movies:
                movie_genres = [g.name for g in movie.genres]
                
                # Check if we can add this movie
                can_add = False
                for genre in movie_genres:
                    if genre in genre_counts and genre_counts[genre] < max_per_genre:
                        can_add = True
                        break
                
                if can_add:
                    result.append(movie.id)
                    for genre in movie_genres:
                        if genre in genre_counts:
                            genre_counts[genre] += 1
                
                if len(result) >= count:
                    break
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting onboarding recommendations: {str(e)}")
            return self._get_fallback_recommendations(db, count)
    
    def get_trending_recommendations(
        self,
        db: Session,
        count: int = 20,
        days: int = 30
    ) -> List[int]:
        """
        Get trending movies based on recent interactions
        
        Args:
            db: Database session
            count: Number of recommendations
            days: Number of days to consider for trending
        
        Returns:
            List of movie IDs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get movies with most recent interactions
            trending = db.query(
                Interaction.movie_id,
                func.count(Interaction.id).label('interaction_count')
            ).filter(
                Interaction.created_at >= cutoff_date
            ).group_by(
                Interaction.movie_id
            ).order_by(
                desc('interaction_count')
            ).limit(count).all()
            
            return [movie_id for movie_id, _ in trending]
            
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {str(e)}")
            return self._get_fallback_recommendations(db, count)
    
    def get_featured_recommendations(
        self,
        db: Session,
        count: int = 20
    ) -> List[int]:
        """
        Get featured/curated movies
        
        Args:
            db: Database session
            count: Number of recommendations
        
        Returns:
            List of movie IDs
        """
        try:
            # Get featured movies
            movies = db.query(Movie).filter(
                Movie.is_featured == True,
                Movie.is_active == True
            ).order_by(
                desc(Movie.rating)
            ).limit(count).all()
            
            # If not enough featured, add top-rated
            if len(movies) < count:
                additional = db.query(Movie).filter(
                    Movie.is_featured == False,
                    Movie.is_active == True
                ).order_by(
                    desc(Movie.rating)
                ).limit(count - len(movies)).all()
                
                movies.extend(additional)
            
            return [m.id for m in movies]
            
        except Exception as e:
            logger.error(f"Error getting featured recommendations: {str(e)}")
            return self._get_fallback_recommendations(db, count)
    
    def _get_fallback_recommendations(
        self,
        db: Session,
        count: int
    ) -> List[int]:
        """Fallback recommendations - top rated movies"""
        try:
            movies = db.query(Movie).filter(
                Movie.is_active == True
            ).order_by(
                desc(Movie.rating),
                desc(Movie.view_count)
            ).limit(count).all()
            
            return [m.id for m in movies]
            
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {str(e)}")
            return []


def get_new_user_recommendations(
    db: Session,
    user_preferences: dict = None,
    count: int = 20
) -> List[int]:
    """Convenience function for new user recommendations"""
    recommender = NewUserRecommender()
    return recommender.get_recommendations(db, user_preferences, count)
