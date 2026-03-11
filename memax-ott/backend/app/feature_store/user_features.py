"""
User Feature Extraction
Extract and manage user features for recommendations
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger
import numpy as np

from app.models.user import User
from app.models.interaction import Interaction
from app.models.watch_history import WatchHistory
from app.models.movie import Movie
from app.models.genre import Genre


class UserFeatureExtractor:
    """Extract features from user behavior"""
    
    def __init__(self, lookback_days: int = 90):
        """
        Initialize feature extractor
        
        Args:
            lookback_days: Number of days to look back for features
        """
        self.lookback_days = lookback_days
    
    def extract_features(
        self,
        user_id: int,
        db: Session
    ) -> Dict[str, any]:
        """
        Extract all features for a user
        
        Args:
            user_id: User ID
            db: Database session
        
        Returns:
            Dict of feature name to value
        """
        try:
            features = {}
            
            # Basic user features
            features.update(self._get_basic_features(user_id, db))
            
            # Behavioral features
            features.update(self._get_behavioral_features(user_id, db))
            
            # Genre preferences
            features.update(self._get_genre_preferences(user_id, db))
            
            # Temporal features
            features.update(self._get_temporal_features(user_id, db))
            
            # Engagement features
            features.update(self._get_engagement_features(user_id, db))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting user features: {str(e)}")
            return {}
    
    def _get_basic_features(self, user_id: int, db: Session) -> Dict:
        """Get basic user features"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {}
        
        # Calculate account age
        account_age_days = (datetime.utcnow() - user.created_at).days
        
        return {
            'account_age_days': account_age_days,
            'is_premium': user.is_premium if hasattr(user, 'is_premium') else False,
            'is_active': user.is_active
        }
    
    def _get_behavioral_features(self, user_id: int, db: Session) -> Dict:
        """Get behavioral features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Interaction counts
        interaction_counts = db.query(
            Interaction.interaction_type,
            func.count(Interaction.id)
        ).filter(
            Interaction.user_id == user_id,
            Interaction.created_at >= cutoff_date
        ).group_by(
            Interaction.interaction_type
        ).all()
        
        features = {
            'total_interactions': sum(count for _, count in interaction_counts),
            'view_count': 0,
            'like_count': 0,
            'complete_count': 0
        }
        
        for interaction_type, count in interaction_counts:
            features[f'{interaction_type}_count'] = count
        
        # Watch history
        watch_count = db.query(WatchHistory).filter(
            WatchHistory.user_id == user_id,
            WatchHistory.watched_at >= cutoff_date
        ).count()
        
        features['watch_count'] = watch_count
        
        # Average watch time
        avg_watch_time = db.query(
            func.avg(WatchHistory.watch_duration)
        ).filter(
            WatchHistory.user_id == user_id,
            WatchHistory.watched_at >= cutoff_date
        ).scalar()
        
        features['avg_watch_time'] = float(avg_watch_time) if avg_watch_time else 0.0
        
        return features
    
    def _get_genre_preferences(self, user_id: int, db: Session) -> Dict:
        """Get genre preference features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Get genre interaction counts
        genre_counts = db.query(
            Genre.name,
            func.count(Interaction.id)
        ).join(
            Movie.genres
        ).join(
            Interaction
        ).filter(
            Interaction.user_id == user_id,
            Interaction.created_at >= cutoff_date
        ).group_by(
            Genre.name
        ).all()
        
        features = {}
        total_interactions = sum(count for _, count in genre_counts)
        
        if total_interactions > 0:
            for genre_name, count in genre_counts:
                # Normalize to percentage
                features[f'genre_pref_{genre_name.lower().replace(" ", "_")}'] = count / total_interactions
        
        # Top genres
        if genre_counts:
            top_genres = sorted(genre_counts, key=lambda x: x[1], reverse=True)[:3]
            features['top_genre'] = top_genres[0][0] if top_genres else None
        
        return features
    
    def _get_temporal_features(self, user_id: int, db: Session) -> Dict:
        """Get temporal behavior features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Get interactions by hour of day
        interactions = db.query(
            Interaction.created_at
        ).filter(
            Interaction.user_id == user_id,
            Interaction.created_at >= cutoff_date
        ).all()
        
        if not interactions:
            return {}
        
        # Calculate hour distribution
        hours = [interaction.created_at.hour for interaction, in interactions]
        
        features = {
            'most_active_hour': max(set(hours), key=hours.count) if hours else 0,
            'activity_variance': float(np.var(hours)) if hours else 0.0
        }
        
        # Weekend vs weekday
        weekday_count = sum(1 for interaction, in interactions if interaction.created_at.weekday() < 5)
        weekend_count = len(interactions) - weekday_count
        
        features['weekday_ratio'] = weekday_count / len(interactions) if interactions else 0.5
        
        return features
    
    def _get_engagement_features(self, user_id: int, db: Session) -> Dict:
        """Get engagement features"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.lookback_days)
        
        # Days since last interaction
        last_interaction = db.query(
            func.max(Interaction.created_at)
        ).filter(
            Interaction.user_id == user_id
        ).scalar()
        
        days_since_last = (datetime.utcnow() - last_interaction).days if last_interaction else 999
        
        # Interaction frequency
        interaction_count = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.created_at >= cutoff_date
        ).count()
        
        interactions_per_day = interaction_count / self.lookback_days if self.lookback_days > 0 else 0
        
        return {
            'days_since_last_interaction': days_since_last,
            'interactions_per_day': interactions_per_day,
            'is_engaged': days_since_last < 7
        }


def get_user_features(user_id: int, db: Session) -> Dict:
    """Convenience function to get user features"""
    extractor = UserFeatureExtractor()
    return extractor.extract_features(user_id, db)
