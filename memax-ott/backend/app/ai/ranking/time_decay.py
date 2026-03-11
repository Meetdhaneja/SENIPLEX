"""
Time Decay for Recommendations
Apply time-based decay to recommendation scores
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from loguru import logger


class TimeDecay:
    """Apply time-based decay to scores"""
    
    def __init__(self, half_life_days: int = 30):
        """
        Initialize time decay
        
        Args:
            half_life_days: Number of days for score to decay to half
        """
        self.half_life_days = half_life_days
        self.decay_constant = np.log(2) / half_life_days
    
    def apply_decay(
        self,
        scores: List[Tuple[int, float]],
        timestamps: Dict[int, datetime],
        reference_time: datetime = None
    ) -> List[Tuple[int, float]]:
        """
        Apply exponential time decay to scores
        
        Args:
            scores: List of (item_id, score) tuples
            timestamps: Dict mapping item_id to timestamp
            reference_time: Reference time for decay calculation (default: now)
        
        Returns:
            List of (item_id, decayed_score) tuples
        """
        if not scores:
            return []
        
        reference_time = reference_time or datetime.utcnow()
        decayed_scores = []
        
        for item_id, score in scores:
            timestamp = timestamps.get(item_id)
            
            if timestamp:
                # Calculate days since timestamp
                days_old = (reference_time - timestamp).total_seconds() / 86400
                
                # Apply exponential decay
                decay_factor = np.exp(-self.decay_constant * days_old)
                decayed_score = score * decay_factor
            else:
                # No timestamp, use original score
                decayed_score = score
            
            decayed_scores.append((item_id, decayed_score))
        
        return decayed_scores
    
    def apply_recency_boost(
        self,
        scores: List[Tuple[int, float]],
        timestamps: Dict[int, datetime],
        boost_window_days: int = 7,
        boost_factor: float = 1.5
    ) -> List[Tuple[int, float]]:
        """
        Boost scores for recent items
        
        Args:
            scores: List of (item_id, score) tuples
            timestamps: Dict mapping item_id to timestamp
            boost_window_days: Number of days to apply boost
            boost_factor: Multiplier for recent items
        
        Returns:
            List of (item_id, boosted_score) tuples
        """
        if not scores:
            return []
        
        now = datetime.utcnow()
        boost_threshold = now - timedelta(days=boost_window_days)
        boosted_scores = []
        
        for item_id, score in scores:
            timestamp = timestamps.get(item_id)
            
            if timestamp and timestamp >= boost_threshold:
                # Apply boost for recent items
                boosted_score = score * boost_factor
            else:
                boosted_score = score
            
            boosted_scores.append((item_id, boosted_score))
        
        return boosted_scores


class TrendingScore:
    """Calculate trending scores based on recent activity"""
    
    def __init__(self, window_days: int = 7):
        """
        Initialize trending scorer
        
        Args:
            window_days: Time window for trending calculation
        """
        self.window_days = window_days
    
    def calculate_trending_scores(
        self,
        item_interactions: Dict[int, List[datetime]],
        reference_time: datetime = None
    ) -> Dict[int, float]:
        """
        Calculate trending scores based on interaction velocity
        
        Args:
            item_interactions: Dict mapping item_id to list of interaction timestamps
            reference_time: Reference time (default: now)
        
        Returns:
            Dict mapping item_id to trending score
        """
        reference_time = reference_time or datetime.utcnow()
        window_start = reference_time - timedelta(days=self.window_days)
        
        trending_scores = {}
        
        for item_id, timestamps in item_interactions.items():
            # Count interactions in window
            recent_interactions = [
                ts for ts in timestamps
                if ts >= window_start
            ]
            
            if recent_interactions:
                # Calculate velocity (interactions per day)
                velocity = len(recent_interactions) / self.window_days
                
                # Apply logarithmic scaling to prevent outliers
                trending_score = np.log1p(velocity)
                
                trending_scores[item_id] = trending_score
            else:
                trending_scores[item_id] = 0.0
        
        # Normalize scores
        if trending_scores:
            max_score = max(trending_scores.values())
            if max_score > 0:
                trending_scores = {
                    k: v / max_score
                    for k, v in trending_scores.items()
                }
        
        return trending_scores


def apply_time_decay_to_recommendations(
    recommendations: List[Tuple[int, float]],
    movie_release_years: Dict[int, int],
    half_life_years: int = 10
) -> List[Tuple[int, float]]:
    """
    Apply time decay based on movie release year
    
    Args:
        recommendations: List of (movie_id, score) tuples
        movie_release_years: Dict mapping movie_id to release year
        half_life_years: Years for score to decay to half
    
    Returns:
        List of (movie_id, decayed_score) tuples
    """
    current_year = datetime.now().year
    decay_constant = np.log(2) / half_life_years
    
    decayed_recommendations = []
    
    for movie_id, score in recommendations:
        release_year = movie_release_years.get(movie_id)
        
        if release_year:
            years_old = current_year - release_year
            decay_factor = np.exp(-decay_constant * max(0, years_old))
            decayed_score = score * decay_factor
        else:
            decayed_score = score
        
        decayed_recommendations.append((movie_id, decayed_score))
    
    return decayed_recommendations
