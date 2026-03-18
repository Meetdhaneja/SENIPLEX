"""
Popularity-Based Baseline Model
Simple popularity-based recommendations
"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from loguru import logger

from app.models.movie import Movie
from app.models.interaction import Interaction


def popularity_score(
    *,
    view_score: float,
    rating_score: float,
    view_weight: float = 0.7,
    rating_weight: float = 0.3,
) -> float:
    return view_weight * view_score + rating_weight * rating_score


class PopularityModel:
    """Popularity-based recommendation model"""
    
    def __init__(self, time_window_days: int = 30):
        """
        Initialize popularity model
        
        Args:
            time_window_days: Time window for calculating popularity
        """
        self.time_window_days = time_window_days
    
    def get_popular_movies(
        self,
        db: Session,
        count: int = 20,
        genre_filter: List[str] = None,
        content_type: str = None
    ) -> List[Tuple[int, float]]:
        """
        Get popular movies
        
        Args:
            db: Database session
            count: Number of movies to return
            genre_filter: Optional list of genres to filter by
            content_type: Optional content type filter ('Movie' or 'TV Show')
        
        Returns:
            List of (movie_id, popularity_score) tuples
        """
        try:
            # Base query
            query = db.query(
                Movie.id,
                Movie.view_count,
                Movie.rating
            ).filter(Movie.is_active == True)
            
            # Apply filters
            if genre_filter:
                from app.models.genre import Genre
                query = query.join(Movie.genres).filter(Genre.name.in_(genre_filter))
            
            if content_type:
                query = query.filter(Movie.content_type == content_type)
            
            # Get movies
            movies = query.all()
            
            # Calculate popularity scores
            if not movies:
                return []
            
            max_views = max(m.view_count for m in movies) or 1
            max_rating = 10.0
            
            scores = []
            for movie in movies:
                # Weighted combination of views and rating
                view_score = movie.view_count / max_views
                rating_score = (movie.rating or 0) / max_rating
                
                score = popularity_score(view_score=view_score, rating_score=rating_score)
                scores.append((movie.id, score))
            
            # Sort by score
            scores.sort(key=lambda x: x[1], reverse=True)
            
            return scores[:count]
            
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []
    
    def get_top_rated(
        self,
        db: Session,
        count: int = 20,
        min_views: int = 10
    ) -> List[Tuple[int, float]]:
        """Get top-rated movies with minimum view threshold"""
        try:
            movies = db.query(Movie).filter(
                Movie.is_active == True,
                Movie.view_count >= min_views
            ).order_by(
                desc(Movie.rating),
                desc(Movie.view_count)
            ).limit(count).all()
            
            return [(m.id, m.rating or 0) for m in movies]
            
        except Exception as e:
            logger.error(f"Error getting top-rated movies: {str(e)}")
            return []


def get_popular_movies(db: Session, count: int = 20) -> List[int]:
    """Convenience function to get popular movie IDs"""
    model = PopularityModel()
    results = model.get_popular_movies(db, count)
    return [movie_id for movie_id, _ in results]
