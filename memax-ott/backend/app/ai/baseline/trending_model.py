"""
Trending Model
Calculate trending movies based on recent activity
"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from app.models.movie import Movie
from app.models.interaction import Interaction


class TrendingModel:
    """Trending movies based on recent activity"""
    
    def __init__(self, window_days: int = 7):
        """
        Initialize trending model
        
        Args:
            window_days: Time window for trending calculation
        """
        self.window_days = window_days
    
    def get_trending_movies(
        self,
        db: Session,
        count: int = 20,
        content_type: str = None
    ) -> List[Tuple[int, float]]:
        """
        Get trending movies based on recent interactions
        
        Args:
            db: Database session
            count: Number of movies to return
            content_type: Optional content type filter
        
        Returns:
            List of (movie_id, trending_score) tuples
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.window_days)
            
            # Get interaction counts in window
            query = db.query(
                Interaction.movie_id,
                func.count(Interaction.id).label('interaction_count')
            ).filter(
                Interaction.created_at >= cutoff_date
            ).group_by(
                Interaction.movie_id
            )
            
            # Join with movies for filtering
            if content_type:
                query = query.join(Movie).filter(
                    Movie.content_type == content_type,
                    Movie.is_active == True
                )
            
            trending_data = query.order_by(
                desc('interaction_count')
            ).limit(count * 2).all()  # Get extra for scoring
            
            if not trending_data:
                return []
            
            # Calculate trending scores
            max_interactions = max(count for _, count in trending_data)
            
            scores = []
            for movie_id, interaction_count in trending_data:
                # Velocity score (interactions per day)
                velocity = interaction_count / self.window_days
                
                # Normalize
                trending_score = np.log1p(velocity) / np.log1p(max_interactions / self.window_days)
                
                scores.append((movie_id, trending_score))
            
            # Sort by score
            scores.sort(key=lambda x: x[1], reverse=True)
            
            return scores[:count]
            
        except Exception as e:
            logger.error(f"Error getting trending movies: {str(e)}")
            return []
    
    def get_rising_movies(
        self,
        db: Session,
        count: int = 20
    ) -> List[Tuple[int, float]]:
        """
        Get rising movies (increasing in popularity)
        
        Args:
            db: Database session
            count: Number of movies to return
        
        Returns:
            List of (movie_id, rise_score) tuples
        """
        try:
            # Compare recent vs previous period
            recent_cutoff = datetime.utcnow() - timedelta(days=self.window_days)
            previous_cutoff = recent_cutoff - timedelta(days=self.window_days)
            
            # Recent interactions
            recent = db.query(
                Interaction.movie_id,
                func.count(Interaction.id).label('recent_count')
            ).filter(
                Interaction.created_at >= recent_cutoff
            ).group_by(
                Interaction.movie_id
            ).subquery()
            
            # Previous interactions
            previous = db.query(
                Interaction.movie_id,
                func.count(Interaction.id).label('previous_count')
            ).filter(
                Interaction.created_at >= previous_cutoff,
                Interaction.created_at < recent_cutoff
            ).group_by(
                Interaction.movie_id
            ).subquery()
            
            # Calculate growth
            results = db.query(
                recent.c.movie_id,
                recent.c.recent_count,
                func.coalesce(previous.c.previous_count, 0).label('previous_count')
            ).outerjoin(
                previous,
                recent.c.movie_id == previous.c.movie_id
            ).all()
            
            # Calculate rise scores
            scores = []
            for movie_id, recent_count, previous_count in results:
                if previous_count > 0:
                    # Growth rate
                    growth = (recent_count - previous_count) / previous_count
                else:
                    # New trending
                    growth = recent_count
                
                if growth > 0:
                    scores.append((movie_id, growth))
            
            # Sort by growth
            scores.sort(key=lambda x: x[1], reverse=True)
            
            return scores[:count]
            
        except Exception as e:
            logger.error(f"Error getting rising movies: {str(e)}")
            return []


def get_trending_movies(db: Session, count: int = 20) -> List[int]:
    """Convenience function to get trending movie IDs"""
    model = TrendingModel()
    results = model.get_trending_movies(db, count)
    return [movie_id for movie_id, _ in results]
