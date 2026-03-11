"""
Movie Feature Extraction
Extract and manage movie features
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger
import numpy as np

from app.models.movie import Movie
from app.models.interaction import Interaction
from app.models.watch_history import WatchHistory


class MovieFeatureExtractor:
    """Extract features from movie data"""
    
    def __init__(self, lookback_days: int = 30):
        """
        Initialize feature extractor
        
        Args:
            lookback_days: Number of days for temporal features
        """
        self.lookback_days = lookback_days
    
    def extract_features(
        self,
        movie_id: int,
        db: Session
    ) -> Dict[str, any]:
        """
        Extract all features for a movie
        
        Args:
            movie_id: Movie ID
            db: Database session
        
        Returns:
            Dict of feature name to value
        """
        try:
            features = {}
            
            # Basic movie features
            features.update(self._get_basic_features(movie_id, db))
            
            # Popularity features
            features.update(self._get_popularity_features(movie_id, db))
            
            # Engagement features
            features.update(self._get_engagement_features(movie_id, db))
            
            # Temporal features
            features.update(self._get_temporal_features(movie_id, db))
            
            # Content features
            features.update(self._get_content_features(movie_id, db))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting movie features: {str(e)}")
            return {}
    
    def _get_basic_features(self, movie_id: int, db: Session) -> Dict:
        """Get basic movie features"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if not movie:
            return {}
        
        # Calculate age
        current_year = datetime.now().year
        movie_age = current_year - movie.release_year if movie.release_year else 0
        
        # Parse duration
        duration_minutes = 0
        if movie.duration:
            if 'min' in movie.duration:
                try:
                    duration_minutes = int(movie.duration.split()[0])
                except:
                    pass
        
        return {
            'content_type': movie.content_type,
            'release_year': movie.release_year or 0,
            'movie_age_years': movie_age,
            'duration_minutes': duration_minutes,
            'rating': movie.rating or 0.0,
            'is_featured': movie.is_featured if hasattr(movie, 'is_featured') else False,
            'genre_count': len(movie.genres),
            'country_count': len(movie.countries)
        }
    
    def _get_popularity_features(self, movie_id: int, db: Session) -> Dict:
        """Get popularity features"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if not movie:
            return {}
        
        return {
            'view_count': movie.view_count,
            'like_count': movie.like_count if hasattr(movie, 'like_count') else 0,
            'popularity_score': np.log1p(movie.view_count)  # Log-scaled
        }
    
    def _get_engagement_features(self, movie_id: int, db: Session) -> Dict:
        """Get engagement features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Recent interactions
        recent_interactions = db.query(Interaction).filter(
            Interaction.movie_id == movie_id,
            Interaction.created_at >= cutoff_date
        ).count()
        
        # Completion rate
        total_views = db.query(WatchHistory).filter(
            WatchHistory.movie_id == movie_id,
            WatchHistory.watched_at >= cutoff_date
        ).count()
        
        completed_views = db.query(WatchHistory).filter(
            WatchHistory.movie_id == movie_id,
            WatchHistory.watched_at >= cutoff_date,
            WatchHistory.completed == True
        ).count()
        
        completion_rate = completed_views / total_views if total_views > 0 else 0.0
        
        # Average watch duration
        avg_watch_duration = db.query(
            func.avg(WatchHistory.watch_duration)
        ).filter(
            WatchHistory.movie_id == movie_id,
            WatchHistory.watched_at >= cutoff_date
        ).scalar()
        
        return {
            'recent_interactions': recent_interactions,
            'completion_rate': completion_rate,
            'avg_watch_duration': float(avg_watch_duration) if avg_watch_duration else 0.0,
            'engagement_score': recent_interactions * completion_rate
        }
    
    def _get_temporal_features(self, movie_id: int, db: Session) -> Dict:
        """Get temporal features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Trending score (recent vs total interactions)
        total_interactions = db.query(Interaction).filter(
            Interaction.movie_id == movie_id
        ).count()
        
        recent_interactions = db.query(Interaction).filter(
            Interaction.movie_id == movie_id,
            Interaction.created_at >= cutoff_date
        ).count()
        
        trending_score = 0.0
        if total_interactions > 0:
            trending_score = recent_interactions / total_interactions
        
        # Days since last interaction
        last_interaction = db.query(
            func.max(Interaction.created_at)
        ).filter(
            Interaction.movie_id == movie_id
        ).scalar()
        
        days_since_last = (datetime.utcnow() - last_interaction).days if last_interaction else 999
        
        return {
            'trending_score': trending_score,
            'days_since_last_interaction': days_since_last,
            'is_trending': trending_score > 0.3 and days_since_last < 7
        }
    
    def _get_content_features(self, movie_id: int, db: Session) -> Dict:
        """Get content-based features"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if not movie:
            return {}
        
        # Genre features
        genres = [g.name for g in movie.genres]
        
        # Country features
        countries = [c.name for c in movie.countries]
        
        # Description length
        description_length = len(movie.description) if movie.description else 0
        
        return {
            'genres': genres,
            'countries': countries,
            'has_description': bool(movie.description),
            'description_length': description_length,
            'has_director': bool(movie.director),
            'has_cast': bool(movie.cast)
        }
    
    def extract_batch_features(
        self,
        movie_ids: List[int],
        db: Session
    ) -> Dict[int, Dict]:
        """
        Extract features for multiple movies
        
        Args:
            movie_ids: List of movie IDs
            db: Database session
        
        Returns:
            Dict mapping movie_id to features dict
        """
        results = {}
        
        for movie_id in movie_ids:
            results[movie_id] = self.extract_features(movie_id, db)
        
        return results


def get_movie_features(movie_id: int, db: Session) -> Dict:
    """Convenience function to get movie features"""
    extractor = MovieFeatureExtractor()
    return extractor.extract_features(movie_id, db)
